from flask import Flask, request, jsonify, render_template, send_from_directory
import googlemaps
import geocoder #Geocoder for location based off of IP
import random #RNG library
import re
from dotenv import load_dotenv
import os

#Addewd line here to test if git command line works
# Load environment variables from the .env file (only keep for dev)
load_dotenv(override=True)
app = Flask(__name__)

# Access the API key
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    raise ValueError("Google Maps API key is missing. Check your .env file.")
print(f"API Key: {API_KEY}")

map_client = googlemaps.Client(API_KEY)

#Function to get (lat, long) using the geocoding library (Wasn't working well)
"""
def get_my_location():
    g = geocoder.ip('me')
    location = (g.latlng[0], g.latlng[1])
    return location
"""

#Function to get (lat, long) using google's geocoding library
def get_my_location():
    g = geocoder.ip('me')
    lat, lng = g.latlng  # Fallback method using IP
    if lat and lng:
        # Optionally use Google Maps Geocoding API for more accuracy
        reverse_geocode = map_client.reverse_geocode((lat, lng))
        if reverse_geocode:
            # You could use reverse_geocode[0] to get more precise information
            return reverse_geocode[0]['geometry']['location']
    return lat, lng  # Fallback location

#Uses a keyword search to find suitable locations based off of geocoding and search radius
def get_surrounding_locations(location, search_string, distance):
    response = map_client.places_nearby(
        location=location,
        keyword=search_string,
        radius=distance
    )
    return response

#Picks at random a place from a list of businesses
def get_random_location(business_list):
    rand = random.randint(0, len(business_list)-1)
    return business_list[rand]

#The following are functions related to getting directions to the location
#Prolly don't need them for the webapp and as such am commenting them out
"""
def get_directions(origin, destination):
    directions = map_client.directions(
        origin=origin,
        destination=f"place_id:{destination}",
        mode='walking'
    )
    return directions

def parse_json(json):
    parsed_steps = []
    leg = json[0].get('legs')[0]
    steps = leg.get('steps')
    for step in steps:
        pattern = re.compile(r'<.*?>')
        cleaned_text = re.sub(pattern, '', step.get('html_instructions'))
        parsed_steps.append(
            {
                "distance": step.get('distance'),
                "html_instructions": cleaned_text,
                "maneuver": step.get('maneuver')
            }
        )
    return parsed_steps
"""

#Loading the index html page ('/' denotes home route)
@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'FRoute_webapp.html')
#def index():
#    return render_template('Froute_webapp.html')



#The following is to actually load the page after a place is found.
@app.route('/get-place', methods=['POST'])
def get_place_route():
    data = request.get_json()
    latitude = data.get('latitude')  # User's latitude
    longitude = data.get('longitude')  # User's longitude
    location = (latitude, longitude)  # Create a tuple for location
    search_string = data.get('search_string', 'restaurant')  # Search keyword (defaults to 'restaurant')
    distance = data.get('distance', 1000)  # Search radius (defaults to 1000 meters)

    # Find nearby places based on the search string and radius
    response = get_surrounding_locations(location, search_string, distance)
    business_list = response.get('results', [])
    
    # If no businesses are found, return an error
    if not business_list:
        return jsonify({"error": "No businesses found"}), 404

    # Pick a random business from the list
    rand_location = get_random_location(business_list)
    
    # Construct the Google Maps URL for the place
    place_url = f"https://www.google.com/maps/place/?q=place_id:{rand_location.get('place_id')}"

    # Return the place name and the Google Maps link
    return jsonify({
        "place_name": rand_location.get('name'),
        "google_maps_url": place_url
    })
@app.route('/get-location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # Use Google Maps or any other service to get more info from coordinates
    location_info = map_client.reverse_geocode((latitude, longitude))
    
    return jsonify(location_info)


#Debugging stuff for when the script is run directly
if __name__ == "__main__":
    app.run(debug=True)
