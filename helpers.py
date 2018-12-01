import requests
import urllib.parse
import constants
import json

from flask import redirect, render_template, request, session
from functools import wraps

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
    return render_template('searched.html', places = buildPlaces(searchQuery), key=constants.KEY, query=searchQuery)
    
def buildPlaces(query):
    requestURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + query + "&key=" + constants.KEY
    results = requests.get(requestURL).json()["results"]
    placeList = list()
    for result in results:
        placeList.append({"name":result["name"], "address":result["formatted_address"]})

    return placeList
