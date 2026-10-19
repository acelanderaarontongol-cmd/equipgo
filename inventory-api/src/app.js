const express = require('express');

// Returns an error string, or null when the payload is valid.
function validateEquipment(body) {
  if (!body || typeof body.name !== 'string' || body.name.trim() === '') {
    return 'name is required';
  }
  if (!Number.isInteger(body.quantity) || body.quantity < 0) {
    return 'quantity must be a non-negative integer';
  }
  return null;
}

// `db` is anything with query(sql, params) -> { rows } (a pg Pool, or a fake in tests).
function createApp(db) {
  const app = express();
  app.use(express.json());

  app.get('/health', (req, res) => res.json({ status: 'ok', service: 'inventory-api' }));

  app.get('/equipment', async (req, res, next) => {
    try {
      const r = await db.query(
        'SELECT id, name, category, quantity, available FROM equipment ORDER BY id'
      );
      res.json(r.rows);
    } catch (e) { next(e); }
  });

  app.get('/equipment/:id', async (req, res, next) => {
    try {
      const r = await db.query(
        'SELECT id, name, category, quantity, available FROM equipment WHERE id = $1',
        [req.params.id]
      );
      if (r.rows.length === 0) return res.status(404).json({ error: 'not found' });
      res.json(r.rows[0]);
    } catch (e) { next(e); }
  });

  app.post('/equipment', async (req, res, next) => {
    const err = validateEquipment(req.body);
    if (err) return res.status(400).json({ error: err });
    try {
      const { name, category = 'general', quantity } = req.body;
      const r = await db.query(
        'INSERT INTO equipment (name, category, quantity, available) VALUES ($1, $2, $3, $3) RETURNING *',
        [name.trim(), category, quantity]
      );
      res.status(201).json(r.rows[0]);
    } catch (e) { next(e); }
  });

  app.put('/equipment/:id', async (req, res, next) => {
    const err = validateEquipment(req.body);
    if (err) return res.status(400).json({ error: err });
    try {
      const { name, category = 'general', quantity } = req.body;
      const r = await db.query(
        `UPDATE equipment SET name = $1, category = $2, quantity = $3,
                available = LEAST(available, $3)
         WHERE id = $4 RETURNING *`,
        [name.trim(), category, quantity, req.params.id]
      );
      if (r.rows.length === 0) return res.status(404).json({ error: 'not found' });
      res.json(r.rows[0]);
    } catch (e) { next(e); }
  });

  // eslint-disable-next-line no-unused-vars
  app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).json({ error: 'internal error' });
  });

  return app;
}

module.exports = { createApp, validateEquipment };
