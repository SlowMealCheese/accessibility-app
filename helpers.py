import requests
import urllib.parse
import constants
import json
import requests

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
	location = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + searchQuery + "&key=" + constants.KEY).json()

	if len(searchQuery)==0:
		return render_template('index.html')
	return render_template('searched.html', key=constants.KEY, query = searchQuery)
