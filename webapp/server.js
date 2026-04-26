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
    
    // Basic validation
    if (!username || !password) {
        return res.render('register', { error: 'Username and password are required' });
    }

    db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, password], function(err) {
        if (err) {
            return res.render('register', { error: 'Username already exists' });
        }
        res.redirect('/login');
    });
});

app.get('/login', (req, res) => {
    res.render('login', { error: null });
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    // INSECURE LOGIN FOR SECURITY TESTING (Intentionally vulnerable to simple SQLi for academic purposes)
    // We will use string interpolation to allow ' OR 1=1 --
    const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
    
    db.get(query, (err, user) => {
        if (err) {
            return res.render('login', { error: 'Database error' });
        }
        if (user) {
            req.session.userId = user.id;
            req.session.username = user.username;
            res.redirect('/dashboard');
        } else {
            res.render('login', { error: 'Invalid username or password' });
        }
    });
});

app.get('/dashboard', (req, res) => {
    if (!req.session.userId) {
        return res.redirect('/login');
    }

    db.get('SELECT * FROM users WHERE id = ?', [req.session.userId], (err, user) => {
        if (err || !user) {
            return res.redirect('/login');
        }
        
        db.all('SELECT * FROM transactions WHERE sender_id = ? OR receiver_username = ? ORDER BY timestamp DESC', [user.id, user.username], (err, transactions) => {
            res.render('dashboard', { 
                username: user.username, 
                balance: user.balance,
                transactions: transactions || [],
                error: req.query.error,
                success: req.query.success
            });
        });
    });
});

app.get('/transfer', (req, res) => {
    if (!req.session.userId) {
        return res.redirect('/login');
    }
    res.render('transfer', { 
        username: req.session.username,
        error: req.query.error,
        success: req.query.success
    });
});

app.post('/transfer', (req, res) => {
    if (!req.session.userId) {
        return res.redirect('/login');
    }

    const { receiver, amount } = req.body;
    const transferAmount = parseFloat(amount);

    if (isNaN(transferAmount) || transferAmount <= 0) {
        return res.redirect('/transfer?error=Invalid transfer amount');
    }

    if (receiver === req.session.username) {
         return res.redirect('/transfer?error=Cannot transfer to yourself');
    }

    db.get('SELECT * FROM users WHERE id = ?', [req.session.userId], (err, sender) => {
        if (sender.balance < transferAmount) {
            return res.redirect('/transfer?error=Insufficient balance');
        }

        db.get('SELECT * FROM users WHERE username = ?', [receiver], (err, receiverUser) => {
            if (!receiverUser) {
                return res.redirect('/transfer?error=Receiver not found');
            }

            // Perform transfer
            db.serialize(() => {
                db.run('BEGIN TRANSACTION');
                db.run('UPDATE users SET balance = balance - ? WHERE id = ?', [transferAmount, sender.id]);
                db.run('UPDATE users SET balance = balance + ? WHERE id = ?', [transferAmount, receiverUser.id]);
                db.run('INSERT INTO transactions (sender_id, receiver_username, amount) VALUES (?, ?, ?)', [sender.id, receiver, transferAmount]);
                db.run('COMMIT', (err) => {
                    if (err) {
                        return res.redirect('/transfer?error=Transfer failed');
                    }
                    res.redirect('/dashboard?success=Transfer successful');
                });
            });
        });
    });
});

app.get('/loans', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    db.get('SELECT * FROM users WHERE id = ?', [req.session.userId], (err, user) => {
        if (err || !user) return res.redirect('/login');
        
        db.all('SELECT * FROM loans WHERE user_id = ? ORDER BY timestamp DESC', [user.id], (err, loans) => {
            res.render('loans', { 
                username: user.username, 
                balance: user.balance,
                loans: loans || [],
                error: req.query.error,
                success: req.query.success
            });
        });
    });
});

app.post('/loan/apply', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    const amount = parseFloat(req.body.amount);
    if (isNaN(amount) || amount <= 0) {
        return res.redirect('/loans?error=Invalid loan amount');
    }

    const userId = req.session.userId;
    const username = req.session.username;

    db.serialize(() => {
        db.run('BEGIN TRANSACTION');
        db.run('UPDATE users SET balance = balance + ? WHERE id = ?', [amount, userId]);
        db.run('INSERT INTO loans (user_id, amount, status) VALUES (?, ?, ?)', [userId, amount, 'unpaid']);
        db.run('INSERT INTO transactions (sender_id, receiver_username, amount) VALUES (NULL, ?, ?)', [username, amount]);
        db.run('COMMIT', (err) => {
            if (err) return res.redirect('/loans?error=Loan application failed');
            res.redirect('/loans?success=Loan approved and funds added to your balance!');
        });
    });
});

app.post('/loan/pay', (req, res) => {
    if (!req.session.userId) return res.redirect('/login');

    const loanId = parseInt(req.body.loan_id);
    const userId = req.session.userId;

    db.get('SELECT * FROM loans WHERE id = ? AND user_id = ? AND status = ?', [loanId, userId, 'unpaid'], (err, loan) => {
        if (err || !loan) return res.redirect('/loans?error=Invalid loan or already paid');

        db.get('SELECT balance FROM users WHERE id = ?', [userId], (err, user) => {
            if (user.balance < loan.amount) {
                return res.redirect('/loans?error=Insufficient balance to pay off this loan');
            }

            db.serialize(() => {
                db.run('BEGIN TRANSACTION');
                db.run('UPDATE users SET balance = balance - ? WHERE id = ?', [loan.amount, userId]);
                db.run('UPDATE loans SET status = ? WHERE id = ?', ['paid', loanId]);
                db.run('INSERT INTO transactions (sender_id, receiver_username, amount) VALUES (?, ?, ?)', [userId, 'Bank (Loan Repayment)', loan.amount]);
                db.run('COMMIT', (err) => {
                    if (err) return res.redirect('/loans?error=Payment failed');
                    res.redirect('/loans?success=Loan paid successfully!');
                });
            });
        });
    });
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
