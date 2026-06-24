from flask import Flask, render_template, request,jsonify,redirect,url_for
import json
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.distance import great_circle

app = Flask(__name__)

OSRM_SERVERS = {"car":"driving","bike":"cycling","foot":"foot"}

geolocator = Nominatim(user_agent="coordinates_finder.")

def get_coords(address_string):
    """Function which turn string address in (lat./long.) form"""
    try:
        location = geolocator.geocode(address_string)
        if location:
            return location.latitude,location.longitude
        return None
    except Exception as e:
        print(f"geopy error: {e}")
        return None

@app.route("/", methods=['GET','POST'])
def home():
    try:
        return render_template("index.html", name="Distance estimator app")
    except Exception as e:
        return e

#MAin calculation stuff
@app.route('/submit', methods=['POST'])
def submit():

    start = request.form.get('start')
    end = request.form.get('end')
    
    start_coords = get_coords(start)
    end_coords = get_coords(end)
    mode = request.form.get('travel_mode')

    if not start or not end:
        print("missing start or end location")
    if mode not in OSRM_SERVERS:
        print("invalid mode of travel provided")


    profile=OSRM_SERVERS[mode]
    osrm_url = f"https://router.project-osrm.org/route/v1/{profile}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=false"

    try:
        response = requests.get(osrm_url)
        osrm_data = response.json()
        
        route = osrm_data["routes"][0]
        distance_meters = route["distance"]
        duration_seconds = route["duration"]
        
        # Convert to human-readable units
        
        distance = round(distance_meters / 1000, 2)
        duration = round(duration_seconds / 60, 1) #its in minutes
                
        # print(f"Distance: {distance} KM")
        if duration>60: #this is because if the ride is above an hour
            duration_hour = round(duration/60,1)
            # print(f"Duration: {duration} hrs")
        # else:
            # print(f"Duration: {duration} mins")

        if duration<60:
            time = f"{duration} Mins"
        elif duration>60:
            time = f"{duration_hour} Hours"
        elif duration==60:
            time = f"{duration_hour} Hour"
        else:
            print("error occured")
        return render_template('form.html', 
            duration=time, 
            distance=distance, 
            start=start, 
            end=end)

    except Exception as e:
        print(f"error: {e}")



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
