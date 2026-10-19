const test = require('node:test');
const assert = require('node:assert');
const { createApp, validateEquipment } = require('../src/app');

const fakeDb = (rows = []) => ({ query: async () => ({ rows }) });

async function withServer(app, fn) {
  const server = app.listen(0);
  try {
    await fn(`http://127.0.0.1:${server.address().port}`);
  } finally {
    server.closeAllConnections?.();
    server.close();
  }
}

test('GET /health returns ok', async () => {
  await withServer(createApp(fakeDb()), async (base) => {
    const res = await fetch(`${base}/health`);
    assert.strictEqual(res.status, 200);
    assert.strictEqual((await res.json()).status, 'ok');
  });
});

test('GET /equipment returns the rows from the database', async () => {
  const rows = [{ id: 1, name: 'Oscilloscope', category: 'electronics', quantity: 3, available: 3 }];
  await withServer(createApp(fakeDb(rows)), async (base) => {
    const body = await (await fetch(`${base}/equipment`)).json();
    assert.deepStrictEqual(body, rows);
  });
});

test('GET /equipment/:id returns 404 when missing', async () => {
  await withServer(createApp(fakeDb([])), async (base) => {
    assert.strictEqual((await fetch(`${base}/equipment/99`)).status, 404);
  });
});

test('POST /equipment rejects an invalid payload with 400', async () => {
  await withServer(createApp(fakeDb()), async (base) => {
    const res = await fetch(`${base}/equipment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: '', quantity: -1 }),
    });
    assert.strictEqual(res.status, 400);
  });
});

test('validateEquipment accepts a good payload and rejects bad ones', () => {
  assert.strictEqual(validateEquipment({ name: 'Multimeter', quantity: 5 }), null);
  assert.ok(validateEquipment({ quantity: 5 }));
  assert.ok(validateEquipment({ name: 'X', quantity: 1.5 }));
});
