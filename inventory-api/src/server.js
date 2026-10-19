const { Pool } = require('pg');
const { createApp } = require('./app');

const pool = new Pool({
  host: process.env.DB_HOST || 'db',
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

createApp(pool).listen(3000, '0.0.0.0', () => console.log('inventory-api listening on 3000'));
