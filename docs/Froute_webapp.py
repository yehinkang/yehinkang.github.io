from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS #(Cross Origin Resource Sharing, allows service to be pinged from all URLs)
import googlemaps #Google Maps API
import geocoder #Geocoder for location based off of IP
import random #RNG library
from dotenv import load_dotenv #Important when testing locally and service is not on render
import os

# Load environment variables from the .env file (only keep for dev)
load_dotenv(override=True)
app = Flask(__name__)
CORS(app) # Using this for troubleshooting allows for access from all URL's
# CORS(app, resources={r"/*": {"origins": "https://yehinkang.github.io/"}}) # Allows for requests to Render from yehinkang.github.io

# Access the API key stored as .env variable
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    raise ValueError("Google Maps API key is missing. Check your .env file.")

#The following is for troubleshooting if the API key changes
#print(f"API Key: {API_KEY}")

map_client = googlemaps.Client(API_KEY)

#Uses a keyword search to find suitable locations based off of geocoding and search radius
def get_surrounding_locations(location, search_string, distance):
    response = map_client.places_nearby(
        location=location,
        keyword=search_string,
        radius=distance,
        open_now=True #only returns places that are currently open
    )
    return response

#Picks at random a place from a list of businesses
def get_random_location(business_list):
    rand = random.randint(0, len(business_list)-1)
    return business_list[rand]

#Loading the index html page ('/' denotes home route)
# @app.route('/')
# def index():
#     return send_from_directory(os.getcwd(), 'FRoute_webapp.html')

#The following line is to be used when testing the program locally.
"""def index():
    return render_template('Froute_webapp.html')"""


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
