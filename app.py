import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd, userHistory, userPortfolio

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded


app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    return apology("TODO")


@app.route("/check", methods=["GET"])
def check():
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    return apology("TODO")


@app.route("/logout")
def logout():
    return apology("TODO")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        # Get stock info and handle error if invalid symbol
        iexQuote = lookup(request.form.get('symbol').strip())
        if not iexQuote:
            return apology('Please provide valid stock symbol')
            # Build string to send to template with stock info
        newQuote = "A share of " + iexQuote["name"] + " (" + iexQuote["symbol"] + ") costs $" + str(iexQuote["price"])
        return render_template('quoted.html', quote=newQuote)
    else:
        return render_template('quote.html')
    return apology("TODO")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
