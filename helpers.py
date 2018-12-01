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
	location = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + searchQuery + "&key=" + constants.KEY).json()

	lat = location["results"][0]["geometry"]["location"]["lat"]
	lng = location["results"][0]["geometry"]["location"]["lng"]

	print(getPlaceIDs(lat,lng,searchQuery))

	if len(searchQuery)==0:
		return render_template('index.html')
	return render_template('searched.html', key=constants.KEY, query = searchQuery)
	
		

def getPlaceIDs(lat, lng, query):
	requestURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + query + "&key=" + constants.KEY
	relevantType = requests.get(requestURL).json()["results"][0]["types"][0]

	requestURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(lat) + "," + str(lng) + "&radius=2000&type=" + relevantType + "&key=" + constants.KEY
	results = requests.get(requestURL).json()["results"]
	
	placeIDs = list()

	for result in results:
		placeIDs.append(result["place_id"])

	return placeIDs
	