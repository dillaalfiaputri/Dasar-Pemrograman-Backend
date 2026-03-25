const mysql = require('mysql2');

const conn = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'viaa',
    database: 'crud_db'
});

conn.connect((err) => {
  if (err) throw err;
  console.log('Terhubung Ke MySQL!');
});

module.exports = conn;