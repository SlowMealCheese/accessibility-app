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
    stocks = db.execute("SELECT * FROM :portfolio WHERE 1", portfolio=userPortfolio(session["user_id"]))
    portfoliocash = db.execute("SELECT cash FROM users WHERE id=:idnum", idnum=session["user_id"])[0]["cash"]
    portfoliovalue = portfoliocash
    # Prepare list of stocks to send to html template
    for stock in stocks:
        price = lookup(stock["symbol"])["price"]
        stock["price"] = usd(price)
        stock["total"] = usd(price*float(stock["shares"]))
        portfoliovalue += (price*float(stock["shares"]))
    # add the cash amount to the end of the list
    stocks.append({'symbol': 'CASH', 'total': usd(portfoliocash)})
    return render_template('index.html', stocks=stocks, total=usd(portfoliovalue))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == 'POST':
        # Error Handling
        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        if not request.form.get("shares"):
            return apology("Provide number of shares to buy",400)

        if not request.form.get("shares").isnumeric():
            return apology("Provide valid number of shares",400)

        if float(request.form.get("shares")) <= 0:
            return apology("Provide valid number of shares",400)

        if float(request.form.get("shares"))%1 > 0:
            return apology("Must provide whole number of shares",400)

        quote = lookup(request.form.get("symbol"))

        if not quote:
            return apology("Provide valid stock symbol")

        # Calculate the cost of the shares and ensure user can afford the purchase
        numshares = int(request.form.get('shares'))
        cost = float(numshares) * quote["price"]
        cash = db.execute("SELECT cash FROM users WHERE id=:idnum", idnum=session["user_id"])[0]['cash']
        if cash > cost:
            idnum = session["user_id"]
            newcash = cash-cost
            db.execute("UPDATE users SET cash = :money WHERE id = :idnum", money=newcash, idnum=idnum)
            # Handles situation where user may already have the stock vs this is a new stock
            if(db.execute("SELECT * FROM :portfolio WHERE symbol=:sym", portfolio=userPortfolio(idnum), sym=quote["symbol"])):
                currentshares = int(db.execute("SELECT shares FROM :portfolio WHERE symbol = :sym",
                                               portfolio=userPortfolio(idnum), sym=quote["symbol"])[0]["shares"])
                db.execute("UPDATE :portfolio SET shares = :newshares WHERE symbol=:sym",
                           portfolio=userPortfolio(idnum), newshares=currentshares+numshares, sym=quote["symbol"])
            else:
                db.execute("INSERT INTO :portfolio ('symbol', 'name', 'shares') VALUES (:sym, :nam, :shar)",
                           portfolio=userPortfolio(idnum), sym=quote["symbol"], nam=quote["name"], shar=numshares)
            db.execute("INSERT INTO :history ('symbol', 'shares', 'price', 'transacted') VALUES (:sym, :shar, :pri, CURRENT_TIMESTAMP)",
                       history=userHistory(idnum), sym=quote["symbol"], shar=numshares, pri=quote["price"])
        else:
            return apology("You can't afford that chief")

        return redirect('/')
    else:
        return render_template('buy.html')


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    newname = request.args.get("username")
    # Checks if user already exists with similar username (non case sensitive)
    dbname = db.execute("SELECT * FROM users WHERE LOWER(username) LIKE LOWER(:username)",
                        username=newname)
    # if user not found return true for free username, else return false for username already taken
    if dbname:
        if dbname[0]["username"].lower() == newname.lower() and len(newname) >= 1:
            return jsonify(False)
    return jsonify(True)


@app.route("/history")
@login_required
def history():
    events = db.execute("SELECT * FROM :history WHERE 1",
                        history=userHistory(session["user_id"]))
    for event in events:
        event['price'] = usd(event['price'])
    portfoliovalue = db.execute("SELECT cash FROM users WHERE id=:idnum",
                                idnum=session["user_id"])[0]["cash"]
    return render_template('history.html', history=events)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


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
    if request.method == "POST":
        # Error Handling
        if not request.form.get('oldpassword'):
            return apology("Must provide old password")
        elif not request.form.get("password"):
            return apology("Must provide new password", 400)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology('New passwords do not match', 400)
        elif not check_password_hash(db.execute("SELECT * FROM users WHERE id=:userid",
                                                userid=session["user_id"])[0]["hash"], request.form.get("oldpassword")):
            return apology("Old Password is incorrect")
        else:
            # Generate new hash and update users table
            newpw = generate_password_hash(request.form.get('password'))
            db.execute("UPDATE users SET hash=:newhash WHERE id=:userid",
                       newhash=newpw, userid=session["user_id"])
            return redirect("/")
    else:
        return render_template("changepassword.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted and matches confirmation
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology('passwords do not match', 400)
        # Just in case naughty user turns off javascript
        else:
            dbname = db.execute("SELECT * FROM users WHERE LOWER(username) LIKE LOWER(:username)",
                                username=request.form.get("username"))
            if dbname:
                return apology('Username already taken', 400)

        # Add username to database
        newusername = request.form.get('username')
        pw = generate_password_hash(request.form.get('password'))
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashh)",
                   username=newusername, hashh=pw)

        user = db.execute("SELECT * FROM users WHERE username = :username",
                          username=newusername)
        # Make new tables for user portfolio and history
        usertable = userPortfolio(user[0]["id"])
        userhistory = userHistory(user[0]["id"])

        db.execute("CREATE TABLE :table ('symbol' char(4) NOT NULL, 'name' varchar(255) NOT NULL, 'shares' int NOT NULL)",
                   table=usertable)
        db.execute("CREATE TABLE :table ('symbol' char(4) NOT NULL, 'shares' int NOT NULL, 'price' float NOT NULL, 'transacted' datetime NOT NULL)",
                   table=userhistory)

        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template('register.html')


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # Check for any possible errors that might slip through javascripts net
    if request.method == 'POST':
        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        if not request.form.get("shares"):
            return apology("Provide number of shares to sell")

        if float(request.form.get("shares")) <= 0:
            return apology("Provide valid number of shares to sell")

        # get quote of stock we will be using
        quote = lookup(request.form.get("symbol"))

        if not quote:
            return apology("Provide valid stock symbol")

        # get the current number of shares and calculate the new shares as well as the new balance
        numshares = int(request.form.get('shares'))
        if numshares > db.execute("SELECT shares FROM :portfolio WHERE symbol=:sym",
                                  portfolio=userPortfolio(session["user_id"]), sym=request.form.get('symbol'))[0]['shares']:
            return apology("You don't have that many shares captain")
        cost = float(numshares) * quote["price"]
        cash = db.execute("SELECT cash FROM users WHERE id=:idnum",
                          idnum=session["user_id"])[0]['cash']

        idnum = session["user_id"]
        newcash = cash+cost
        db.execute("UPDATE users SET cash = :money WHERE id = :idnum",
                   money=newcash, idnum=idnum)
        currentshares = int(db.execute("SELECT shares FROM :portfolio WHERE symbol = :sym",
                                       portfolio=userPortfolio(idnum), sym=quote["symbol"])[0]["shares"])
        # Handles if you are selling all or only some of your shares to prevent a stock showing up that you own 0 of
        if currentshares > numshares:
            db.execute("UPDATE :portfolio SET shares = :newshares WHERE symbol=:sym",
                       portfolio=userPortfolio(idnum), newshares=currentshares-numshares, sym=quote["symbol"])
        else:
            db.execute("DELETE FROM :portfolio WHERE symbol=:sym",
                       portfolio=userPortfolio(idnum), sym=quote["symbol"])
        db.execute("INSERT INTO :history ('symbol', 'shares', 'price', 'transacted') VALUES (:sym, :shar, :pri, CURRENT_TIMESTAMP)",
                   history=userHistory(idnum), sym=quote["symbol"], shar=-numshares, pri=quote["price"])

        return redirect('/')
    else:
        stocks = db.execute("SELECT * FROM :portfolio WHERE 1",
                            portfolio=userPortfolio(session["user_id"]))
        symbols = []
        for stock in stocks:
            symbols.append(stock["symbol"])
        return render_template('sell.html', symbols=symbols)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
