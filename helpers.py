from functools import wraps
from flask import redirect, render_template, session
from flask import session
import yfinance as yf


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", top=code, bottom=message), code

def login_required(f):
    """Decorator to require login for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def lookup(symbol):
    """Look up quote for symbol."""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        price = data['Close'].iloc[-1]
        return {
            "symbol": symbol.upper(),
            "price": price,
            "name": stock.info.get('longName', 'Unknown')
        }
    except Exception:
        return None