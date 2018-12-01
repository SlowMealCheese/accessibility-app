import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session, g
from flask_session import Session
import sqlite3
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, search

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
DATABASE = 'places.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Routes

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method=="GET":
		return render_template('index.html');
	else:
		return search(request.form.get('searchAddress'));

@app.route("/report", methods=["GET"])
def report():
	userType = request.args.get('userType')
	return render_template('report.html')
	

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
#for code in default_exceptions:
#    app.errorhandler(code)(errorhandler)
