import os

import math
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask import g
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, usd, lookup, apology

app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

app.config['DATABASE'] = 'FIRE.db'

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Function to get a database connection per request
def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect('FIRE.db')
		g.db.row_factory = sqlite3.Row
	return g.db

# Ensure templates are auto-reloaded
@app.before_request
def before_request():
	"""Connect to the database before each request."""
	g.db = get_db()


# Close the database connection after each request
@app.teardown_appcontext
def close_db(error):
	db = g.pop('db', None)
	if db is not None:
		db.close()

@app.route('/')
def index():
	"""Show portfolio of stocks"""
	if 'user_id' not in session:
		return redirect('/login')

	user_id = session['user_id']
	user = g.db.execute("SELECT * FROM users WHERE id = ?", user_id)
	if not user:
		return apology("User not found", 404)

	accounts_results = g.db.execute("SELECT * FROM accounts WHERE user_id = ?", user_id)
	accounts = accounts_results

	net_worth = sum(account['balance'] for account in accounts)

	top_investment_results = g.db.execute("""SELECT symbol, SUM(CASE WHEN type = 'BUY' THEN shares ELSE -shares END) AS total_shares
		FROM transactions WHERE user_id = ? GROUP BY symbol ORDER BY total_shares DESC LIMIT 5""", user_id)
	top_investments = []
	for row in top_investment_results:
		symbol = row['symbol']
		if symbol:
			stock = lookup(symbol)
			if stock:
				top_investments.append({
					'symbol': stock['symbol'],
					'name': stock['name'],
					'price': stock['price'],
					'shares': row['total_shares'],
					'value': row['total_shares'] * stock['price']
				})

	fire_results = g.db.execute("SELECT fire_number, time_to_fire FROM users WHERE id = ?", user_id)
	fire_number = fire_results[0]['fire_number'] if fire_results else None
	years_to_fire = fire_results[0]['time_to_fire'] if fire_results else None

	return render_template("index.html", user=user[0], accounts=accounts, net_worth=usd(net_worth), 
						   top_investments=top_investments, fire_number=usd(fire_number) if fire_number else None, years_to_fire=years_to_fire if years_to_fire else None)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = g.db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", transactions=rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

        rows = g.db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmation")

    if not username:
        return apology("must provide username", 400)
    if not password:
        return apology("must provide password", 400)
    if not confirm_password:
        return apology("must confirm password", 400)
    if password != confirm_password:
        return apology("passwords must match", 400)
	
    rows = g.db.execute("SELECT * FROM users WHERE username = ?", username)
    if rows:
        return apology("username already registered", 400)

    hash_pw = generate_password_hash(password)
    g.db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)
    rows = g.db.execute("SELECT * FROM users WHERE username = ?", username)
    session["user_id"] = rows[0]["id"]

    return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

@app.route("/open", methods=["GET", "POST"])
@login_required
def open_account():
	"""Open a new account"""
	if request.method == "POST":
		account_type = request.form.get("account_type")
		if account_type == 'CASH':
			if g.db.execute("SELECT * FROM accounts WHERE user_id = ? AND type = 'CASH'", session["user_id"]).fetchone():
				return apology("Cash account already exists", 400)
		elif account_type not in ['CASH', 'SAVINGS', 'BROKERAGE', 'RETIREMENT', 'HEALTH']:
			return apology("Invalid account type", 400)
		if not account_type:
			return apology("must provide account type", 400)
		account_name = request.form.get("account_name")
		if not account_name:
			return apology("must provide account name", 400)
		initial_balance = request.form.get("initial_balance")
		try:
			initial_balance = float(initial_balance)
			if initial_balance < 0:
				raise ValueError
		except (ValueError, TypeError):
			return apology("invalid initial balance", 400)

		user_id = session["user_id"]
		g.db.execute("INSERT INTO accounts (user_id, name, type, balance) VALUES (?, ?, ?, ?)", user_id, account_name, account_type, initial_balance)
		g.db.commit()
		flash("Account created successfully", "success")
		return redirect("/accounts")

	return render_template("accounts.html")

@app.route("/accounts", methods=["GET", "POST"])
@login_required
def accounts():
	"""Display user accounts"""
	
	user_id = session["user_id"]
	user = g.db.execute("SELECT * FROM users WHERE id = ?", user_id)
	if not user:
		return apology("User not found", 404)
	
	accounts_results = g.db.execute("SELECT * FROM accounts WHERE user_id = ?", user_id)
	
	return render_template("accounts.html", user=user[0], accounts=accounts_results)

@app.route('/invest', methods=['GET', 'POST'])
@login_required
def invest():
	"""Invest in stocks"""
	if request.method == 'GET':
		return render_template('invest.html')
	if request.method == 'POST':
		symbol = request.form.get('symbol')
		symbol = symbol.upper()
		shares = request.form.get('shares')
		account = request.form.get('account')

		if not symbol or not shares:
			return apology("must provide symbol and shares", 400)
		if not symbol.isalpha():
			return apology("invalid stock symbol", 400)
		if not shares.isdigit():
			return apology("invalid number of shares", 400)
		try:
			shares = int(shares)
			if shares <= 0:
				raise ValueError
		except ValueError:
			return apology("invalid number of shares", 400)

		stock = lookup(symbol)
		if stock is None:
			return apology("invalid stock symbol", 400)

		price = stock['price']
		total = shares * price
		user_id = session["user_id"]

		account_balance = g.db.execute("SELECT balance FROM accounts WHERE user_id = ? AND name = ? AND type = 'CASH'", user_id, account)
		if not account_balance or account_balance[0]['balance'] < total:
			return apology("not enough cash in account", 400)
		
		g.db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type, account) VALUES (?, ?, ?, ?, 'BUY', ?)", user_id, symbol, shares, price, account)
		g.db.execute("""UPDATE accounts SET balance = balance - ? WHERE user_id = ? AND name = ?""", total, user_id, account)
		g.db.commit()

		flash(f"Bought {shares} shares of {stock['symbol']} at {usd(stock['price'])}")
		return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
	"""Sell shares of stock"""
	if request.method == "GET":
		return render_template("sell.html")
	if request.method == "POST":
		symbol = request.form.get("symbol")
		symbol = symbol.upper()
		shares = request.form.get("shares")
		account = request.form.get("account")

		if not symbol or not shares:
			return apology("must provide symbol and shares", 400)
		if not symbol.isalpha():
			return apology("invalid stock symbol", 400)
		if not shares.isdigit():
			return apology("invalid number of shares", 400)
		try:
			shares = int(shares)
			if shares <= 0:
				raise ValueError
		except ValueError:
			return apology("invalid number of shares", 400)

		# logic to sell the stock
		user_id = session["user_id"]
		result = g.db.execute("SELECT symbol, SUM(CASE WHEN type = 'BUY' THEN shares ELSE -shares END) AS total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", (user_id, symbol))
		if not result or result[0]['total_shares'] < shares:
			return apology("not enough shares to sell", 400)
		
		stock = lookup(symbol)
		if stock is None:
			return apology("invalid stock symbol", 400)
		
		price = stock['price']
		total = shares * price

		account_balance = g.db.execute("SELECT balance FROM accounts WHERE user_id = ? AND name = ? AND type = 'CASH'", user_id, account)
		if not account_balance:
			return apology("account not found", 400)
		
		# Record the transaction
		g.db.execute("INSERT INTO transactions (user_id, symbol, shares, price, type, account) VALUES (?, ?, ?, ?, 'SELL', ?)", user_id, symbol, -shares, price, account)
		g.db.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ? AND name = ? AND type = 'CASH'", total, user_id, account)
		g.db.commit()
		
		flash(f"Sold {shares} shares of {stock['symbol']} at {usd(stock['price'])}")
		return redirect("/")

	return render_template("sell.html")

@app.route("/research", methods=["GET", "POST"])
@login_required
def research():
    """Get stock info."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol = symbol.upper()
        
        if not symbol:
            return apology("must provide symbol", 400)
        if not symbol.isalpha():
            return apology("invalid stock symbol", 400)

        stock = lookup(symbol)
        if stock is None:
            return apology("Invalid symbol")

        return render_template("researched.html",
                               name=stock["name"],
                               symbol=stock["symbol"],
                               price=usd(stock["price"]))
    else:
        return render_template("research.html")

@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
	if request.method == 'POST':
		# Process calculator input here
		income = float(request.form.get('income'))
		expenses = float(request.form.get('expenses'))
		savings_rate = float(request.form.get('savings_rate'))
		net_worth = float(request.form.get('net_worth'))
		swr = float(request.form.get('SWR'))
		apr = float(request.form.get('APR'))
		# Perform calculations and render results
		fire_number = expenses / (swr / 100) if swr else None
		if fire_number and net_worth > 0 and apr > 0:
			r = apr / 100
			try:
				years_to_fire = math.log(fire_number / net_worth) / math.log(1 + r)
				if years_to_fire < 0:
					years_to_fire = None
			except (ValueError, ZeroDivisionError):
				years_to_fire = None
		# Store results in the database
		g.db.execute('UPDATE users SET fire_number = ?, time_to_fire = ? WHERE id = ?', fire_number, years_to_fire, session["user_id"])
		g.db.commit()
		return render_template('calculator.html', fire_number=fire_number, years_to_fire=years_to_fire)

	return render_template('calculator.html')


@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
	if request.method == 'POST':
		amount = request.form.get('amount', '').strip()
		try:
			amount = float(amount)
			if amount <= 0:
				raise ValueError("Amount must be positive")
		except (ValueError, TypeError):
			flash('Invalid amount', 'error')
			return redirect('/deposit')
		
		user_id = session['user_id']

		# Log the transaction
		g.db.execute(
			"INSERT INTO transactions (user_id, symbol, shares, price, type, account) VALUES (?, 'CASH', 1, ?, 'DEPOSIT', 'CASH')",
			user_id, amount
		)

		# Check if a CASH account already exists
		existing = g.db.execute(
			"SELECT * FROM accounts WHERE user_id = ? AND type = 'CASH'",
			user_id
		).fetchone()

		if not existing:
			# Insert a new CASH account
			g.db.execute(
				"INSERT INTO accounts (user_id, name, type, balance) VALUES (?, 'Cash Account', 'CASH', ?)",
				user_id, amount
			)
		else:
			# Update existing CASH account balance
			g.db.execute(
				"UPDATE accounts SET balance = balance + ? WHERE user_id = ? AND type = 'CASH'",
				amount, user_id
			)

		g.db.commit()
		flash('Deposit successful', 'success')
		return redirect('/')

	# If GET request
	return render_template('deposit.html')
