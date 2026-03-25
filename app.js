const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const db = require('./db');

const app = express();
const port = 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static('public'));

app.use(bodyParser.urlencoded({ extended: false }));

// READ: Tampilkan semua user
app.get('/', (req, res) => {
    db.query('SELECT * FROM users', (err, results) => {
        if (err) throw err;
        res.render('index', { users: results });
    });
});

// CREATE: Form tambah
app.get('/add', (req, res) => {
    res.render('add');
});

app.post('/add', (req, res) => {
    const { name, email } = req.body;
    db.query('INSERT INTO users SET ?', { name, email }, (err) => {
        if (err) throw err;
        res.redirect('/');
    });
});

// UPDATE: Form edit
app.get('/edit/:id', (req, res) => {
    const id = req.params.id;
    db.query('SELECT * FROM users WHERE id = ?', [id], (err, results) => {
        if (err) throw err;
        res.render('edit', { user: results[0] });
    });
});

app.post('/edit/:id', (req, res) => {
    const { name, email } = req.body;
    const id = req.params.id;
    db.query('UPDATE users SET name = ?, email = ? WHERE id = ?', [name, email, id], (err) => {
        if (err) throw err;
        res.redirect('/');
    });
});

// DELETE
app.get('/delete/:id', (req, res) => {
    const id = req.params.id;
    db.query('DELETE FROM users WHERE id = ?', [id], (err) => {
        if (err) throw err;
        res.redirect('/');
    });
});

app.listen(port, () => {
    console.log(`App running at http://localhost:${port}`);
});