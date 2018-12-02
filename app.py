import os
import sqlite3
import urllib.parse
import requests
import json


from flask import Flask, flash, jsonify, redirect, render_template, request, session, g
from flask_session import Session
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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


# Helper functions

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def search(searchAddress):
    searchWords= searchAddress.split()
    searchQuery = ''
    for word in searchWords:
        searchQuery = searchQuery+word+ '+'
    searchQuery = searchQuery[:-1]

    if len(searchQuery)==0:
        return render_template('index.html')
    return render_template('searched.html', places = buildPlaces(searchQuery), key=KEY, query=searchQuery)
    
def buildPlaces(query):
    requestURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + query + "&key=" + KEY
    results = requests.get(requestURL).json()["results"]
    placeList = list()
    for result in results:
        q = query_db('SELECT * FROM places WHERE place_id = ?', (result["place_id"],))
        if q:
            q = q[0]
            placeList.append({"name":result["name"], "address":result["formatted_address"], "placeid":result["place_id"], 
                              "wheelchair":q["wheelchair"], "bathroom_access":q["bathroom_access"],
                              "door_width":q["door_width"], "table_height":q["table_height"]})
        else:
            placeList.append({"name":result["name"], "address":result["formatted_address"], "placeid":result["place_id"]})
    return placeList


# Routes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method=="GET":
        Places = query_db('SELECT * FROM places')
        return render_template('index.html', Places=Places, KEY=KEY, mainpage=True);
    else:
        return search(request.form.get('searchAddress'));

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method=="GET":
        userType = request.args.get('userType')
        print(request.form.get('place_name'))
        print(request.form.get('place_id'))
        return render_template('report.html', place_name=request.args.get("place_name"), place_id=request.args.get("place_id"))
    else:
        place_id = request.form.get("place_id")
        wheelchair = request.form.get("wheelchair")
        bathroom_access = request.form.get("bathroom_access")
        door_width = request.form.get("door_width")
        table_height = request.form.get("table_height")

        q = query_db('SELECT * FROM places WHERE place_id=?', (place_id,))
        if (q):
            query_db('UPDATE places SET wheelchair=?, bathroom_access=?, door_width=?, table_height=? WHERE place_id=?',
                     (wheelchair, bathroom_access, door_width, table_height, place_id))
        else:
            query_db('INSERT INTO places (place_id, wheelchair, bathroom_access, door_width, table_height) VALUES (?, ?, ?, ?, ?)',
                     (place_id, wheelchair, bathroom_access, door_width, table_height))

        return render_template("index.html", success_message="Thank you! Your report was successfully logged!")

@app.route("/nextpage")

@app.route("/mission", methods=["GET", "POST"])
def mission():
    return render_template('mission.html')

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
#for code in default_exceptions:
#    app.errorhandler(code)(errorhandler)
