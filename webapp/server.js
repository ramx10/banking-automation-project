const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const path = require('path');
const db = require('./database');

const app = express();
const PORT = 3000;

// Setup EJS and static files
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: 'bank_secret_key',
    resave: false,
    saveUninitialized: true
}));

// Routes
app.get('/', (req, res) => {
    res.redirect('/login');
});

app.get('/register', (req, res) => {
    res.render('register', { error: null });
});

app.post('/register', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.render('register', { error: 'Username and password are required' });
    }

    try {
        db.prepare('INSERT INTO users (username, password) VALUES (?, ?)').run(username, password);
        res.redirect('/login');
    } catch (err) {
        res.render('register', { error: 'Username already exists' });
    }
});

app.get('/login', (req, res) => {
    res.render('login', { error: null });
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;

    // INSECURE LOGIN FOR SECURITY TESTING (Intentionally vulnerable to SQLi for academic purposes)
    try {
        const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
        const user = db.prepare(query).get();

        if (user) {
            req.session.userId = user.id;
            req.session.username = user.username;
            res.redirect('/dashboard');
        } else {
            res.render('login', { error: 'Invalid username or password' });
        }
    } catch (err) {
        res.render('login', { error: 'Database error' });
    }
});

app.get('/dashboard', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    try {
        const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.session.userId);
        if (!user) return res.redirect('/login');

        const transactions = db.prepare(
            'SELECT * FROM transactions WHERE sender_id = ? OR receiver_username = ? ORDER BY timestamp DESC'
        ).all(user.id, user.username);

        res.render('dashboard', {
            username: user.username,
            balance: user.balance,
            transactions: transactions || [],
            error: req.query.error,
            success: req.query.success
        });
    } catch (err) {
        res.redirect('/login');
    }
});

app.get('/transfer', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');
    res.render('transfer', {
        username: req.session.username,
        error: req.query.error,
        success: req.query.success
    });
});

app.post('/transfer', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    const { receiver, amount } = req.body;
    const transferAmount = parseFloat(amount);

    if (isNaN(transferAmount) || transferAmount <= 0) {
        return res.redirect('/transfer?error=Invalid transfer amount');
    }

    if (receiver === req.session.username) {
        return res.redirect('/transfer?error=Cannot transfer to yourself');
    }

    try {
        const sender = db.prepare('SELECT * FROM users WHERE id = ?').get(req.session.userId);
        if (sender.balance < transferAmount) {
            return res.redirect('/transfer?error=Insufficient balance');
        }

        const receiverUser = db.prepare('SELECT * FROM users WHERE username = ?').get(receiver);
        if (!receiverUser) {
            return res.redirect('/transfer?error=Receiver not found');
        }

        // Perform transfer atomically
        const transfer = db.transaction(() => {
            db.prepare('UPDATE users SET balance = balance - ? WHERE id = ?').run(transferAmount, sender.id);
            db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?').run(transferAmount, receiverUser.id);
            db.prepare('INSERT INTO transactions (sender_id, receiver_username, amount) VALUES (?, ?, ?)').run(sender.id, receiver, transferAmount);
        });
        transfer();

        res.redirect('/dashboard?success=Transfer successful');
    } catch (err) {
        res.redirect('/transfer?error=Transfer failed');
    }
});

app.get('/loans', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    try {
        const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.session.userId);
        if (!user) return res.redirect('/login');

        const loans = db.prepare('SELECT * FROM loans WHERE user_id = ? ORDER BY timestamp DESC').all(user.id);

        res.render('loans', {
            username: user.username,
            balance: user.balance,
            loans: loans || [],
            error: req.query.error,
            success: req.query.success
        });
    } catch (err) {
        res.redirect('/dashboard');
    }
});

app.post('/loan/apply', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    const amount = parseFloat(req.body.amount);
    if (isNaN(amount) || amount <= 0) {
        return res.redirect('/loans?error=Invalid loan amount');
    }

    const userId = req.session.userId;
    const username = req.session.username;

    try {
        const applyLoan = db.transaction(() => {
            db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?').run(amount, userId);
            db.prepare('INSERT INTO loans (user_id, amount, status) VALUES (?, ?, ?)').run(userId, amount, 'unpaid');
            db.prepare('INSERT INTO transactions (sender_id, receiver_username, amount) VALUES (NULL, ?, ?)').run(username, amount);
        });
        applyLoan();

        res.redirect('/loans?success=Loan approved and funds added to your balance!');
    } catch (err) {
        res.redirect('/loans?error=Loan application failed');
    }
});

app.post('/loan/pay', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    const loanId = parseInt(req.body.loan_id);
    const userId = req.session.userId;

    try {
        const loan = db.prepare('SELECT * FROM loans WHERE id = ? AND user_id = ? AND status = ?').get(loanId, userId, 'unpaid');
        if (!loan) return res.redirect('/loans?error=Invalid loan or already paid');

        const user = db.prepare('SELECT balance FROM users WHERE id = ?').get(userId);
        if (user.balance < loan.amount) {
            return res.redirect('/loans?error=Insufficient balance to pay off this loan');
        }

        const payLoan = db.transaction(() => {
            db.prepare('UPDATE users SET balance = balance - ? WHERE id = ?').run(loan.amount, userId);
            db.prepare('UPDATE loans SET status = ? WHERE id = ?').run('paid', loanId);
            db.prepare('INSERT INTO transactions (sender_id, receiver_username, amount) VALUES (?, ?, ?)').run(userId, 'Bank (Loan Repayment)', loan.amount);
        });
        payLoan();

        res.redirect('/loans?success=Loan paid successfully!');
    } catch (err) {
        res.redirect('/loans?error=Payment failed');
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
