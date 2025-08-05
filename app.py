
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session

app = Flask(__name__)

# Function to get a database connection per request
def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect('FIRE.db')
		g.db.row_factory = sqlite3.Row
	return g.db

# Close the database connection after each request
@app.teardown_appcontext
def close_db(error):
	db = g.pop('db', None)
	if db is not None:
		db.close()

@app.route('/')
def index():
	return render_template('index.html')