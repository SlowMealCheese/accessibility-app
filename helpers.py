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
    return buildPlaces(searchQuery)
	
    
def buildPlaces(query):
	requestURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + query + "&key=" + constants.KEY
	returnedData = requests.get(requestURL).json()
	results = returnedData["results"]
	try:
		token = returnedData["next_page_token"]
	except:
		return render_template('index.html')
	placeList = list()
	for result in results:
		placeList.append({"name":result["name"], "address":result["formatted_address"], "placeid":result["place_id"]})
	return render_template('searched.html', places = placeList, key=constants.KEY, query=query, newQuery=query+"&pageToken="+token)
