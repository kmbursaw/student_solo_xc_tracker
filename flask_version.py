import folium
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# OpenSky API Configuration
API_URL = "https://opensky-network.org/api/states/all"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solo Student Cross-Country Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #00008B;
            color: white;
            text-align: center;
        }
        .map {
            height: 500px;
            width: 100%;
            margin: 20px auto;
        }
        .form-container {
            margin: 20px auto;
        }
        label, select, input {
            font-size: 1.2em;
            margin: 5px;
        }
    </style>
</head>
<body>
    <h1>Solo Student Cross-Country Tracker</h1>
    <div class="form-container">
        <form method="GET" action="/">
            <label for="tail_number">Enter Tail Number:</label>
            <input type="text" id="tail_number" name="tail_number" placeholder="e.g., N####" required>
            <label for="basemap">Choose a Basemap:</label>
            <select id="basemap" name="basemap">
                <option value="OpenStreetMap">OpenStreetMap</option>
                <option value="CartoDB Positron">CartoDB Positron</option>
                <option value="CartoDB Dark_Matter">CartoDB Dark_Matter</option>
            </select>
            <button type="submit">Track</button>
        </form>
    </div>
    <div id="map" class="map">{{ map_html|safe }}</div>
    {% if info %}
    <div class="info">
        <h2>Aircraft Information</h2>
        <p><strong>Callsign:</strong> {{ info['callsign'] }}</p>
        <p><strong>Origin Country:</strong> {{ info['origin_country'] }}</p>
        <p><strong>Airspeed:</strong> {{ info['velocity_knots']|default('Data not available') }} knots</p>
        <p><strong>Altitude:</strong> {{ info['altitude_feet']|default('Data not available') }} feet</p>
        <p><strong>Heading:</strong> {{ info['heading']|default('Data not available') }}°</p>
    </div>
    {% endif %}
</body>
</html>
"""

# Function to fetch flight info from API
def fetch_flight_info(callsign):
    if not callsign:
        return None
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        flights = data.get("states", [])
        for flight in flights:
            if flight[1] and callsign.upper() in flight[1].strip():
                velocity_in_mps = flight[9]
                velocity_in_knots = velocity_in_mps * 1.94384 if velocity_in_mps else None
                altitude_in_meters = flight[13]
                altitude_in_feet = altitude_in_meters * 3.28084 if altitude_in_meters else None
                heading = flight[10]
                return {
                    "callsign": flight[1],
                    "origin_country": flight[2],
                    "latitude": flight[6],
                    "longitude": flight[5],
                    "velocity_mps": velocity_in_mps,
                    "velocity_knots": velocity_in_knots,
                    "altitude_meters": altitude_in_meters,
                    "altitude_feet": altitude_in_feet,
                    "heading": heading,
                }
        return None
    except requests.exceptions.RequestException as e:
        return None

@app.route("/")
def index():
    tail_number = request.args.get("tail_number", "")
    basemap = request.args.get("basemap", "OpenStreetMap")

    # Initialize Map
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles=basemap)

    info = None
    if tail_number:
        info = fetch_flight_info(tail_number)
        if info and info["latitude"] and info["longitude"]:
            folium.Marker(
                location=[info["latitude"], info["longitude"]],
                popup=(
                    f"Callsign: {info['callsign']}\n"
                    f"Origin Country: {info['origin_country']}\n"
                    f"Airspeed: {info['velocity_knots']:.2f} knots\n"
                    f"Altitude: {info['altitude_feet']:.2f} feet\n"
                    f"Heading: {info['heading']:.2f}°"
                ),
                icon=folium.Icon(color="blue", icon="plane"),
            ).add_to(m)

    map_html = m._repr_html_()
    return render_template_string(HTML_TEMPLATE, map_html=map_html, info=info)

if __name__ == "__main__":
    app.run(debug=True)
