import os
import sqlite3
import requests

from flask import Flask, flash, jsonify, redirect, render_template, request, session, g
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, search
from constants import KEY


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

def query_db(query, args=()):

    db = getattr(g, '_database', None)
    
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))
        
    db.row_factory = make_dicts

    cur = db.execute(query, args)

    rv = cur.fetchall()

    db.commit()
    cur.close()
    return rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Routes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method=="GET":
        Places = query_db('SELECT * FROM places')
        return render_template('index.html', Places=Places, KEY=KEY);
    else:
        return search(request.form.get('searchAddress'));

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method=="GET":
        userType = request.args.get('userType')
        return render_template('report.html', place_id=place_id)
    else:
        query_db('INSERT INTO places (place_id, wheelchair, bathroom_access, door_width, table_height) VALUES (?, ?, ?, ?, ?)', 
                 (request.form.get("place_id"), request.form.get("wheelchair"), request.form.get("bathroom_access"),
                  request.form.get("door_width"), request.form.get("table_height")))
        return redirect("/")

@app.route("/mission", methods=["GET", "POST"])
def mission():
    return render_template('mission.html')

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
#for code in default_exceptions:
#    app.errorhandler(code)(errorhandler)
