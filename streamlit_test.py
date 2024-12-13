#imports needed libraries
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

#function to add background color to page
def add_background(color="#00008B"):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </sytle>
        """,
        unsafe_allow_html=True
    )

#adds background color
add_background("#00008B")

#funciton to add title typography, color, and size
def title_color(color="#FFFFFF", font_family="Roboto", font_size="52"):
    st.markdown(
        f"""
        <style>
        h1 {{
            color: {color};
            font-family: {font_family}, sans-serif;
            font-size: {font_size};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

#adds title color
title_color("#FFFFFF","Roboto","52px")

# OpenSky API Configuration
API_URL = "https://opensky-network.org/api/states/all"

# Title
st.title("Solo Student Cross-Country Tracker")

#markdown text section to explain application, directions for use, and planned future functions
st.markdown(
    """
    <style>
    .white-text {
        color: white;
    }
    </style>
    <div class="white-text">
        This application is designed for the Certified Flight Instructor (CFI) that is sending their students on solo cross-country flights. It is designed to track their students by tail number on the aircraft.
    </div>
    """,
    unsafe_allow_html=True
)

#adds space for readability
st.write("")

st.markdown(
    """
    <style>
    .white-text {
        color: white;
    }
    </style>
    <div class="white-text">
        To use this application, simply type the tail number of the student's aircraft into the sidebar and hit enter. Your student's aircraft will be displayed with a marker on the chart with altitude, airspeed and direction. Additionally, if the user clicks on the marker, the marker will display the data on the map itself as well.
    </div>
    """,
    unsafe_allow_html=True
)

#adds space for readability
st.write("")

st.markdown(
    """
    <style>
    .white-text {
        color: white;
    }
    </style>
    <div class="white-text">
        This map is a full slippy web map with functionality like any other webmap that users interact with on a daily basis. The sidebar also will allow the Instructor to choose one of three basemaps, the third one being ideal for night operations.
    </div>
    """,
    unsafe_allow_html=True
)

#adds space for readability
st.write("")

st.markdown(
    """
    <style>
    .white-text {
        color: white;
    }
    </style>
    <div class="white-text">
        Further functionality is planned with a free service to text the Instructor, (who will provide a phone number), when the student lands and the altitude reads 0ft. 
    </div>
    """,
    unsafe_allow_html=True
)


#creates sidebar and basemap dropdown
with st.sidebar:
    st.header("Basemap Options")
    basemap_options = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB Positron": "CartoDB Positron",
        "CartoDB Dark_Matter": "CartoDB Dark_Matter",
    }
    selected_basemap = st.selectbox("Choose a basemap:", list(basemap_options.keys()))


#initializes Map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles=basemap_options[selected_basemap])



#adds text entry box for tailnumber entry
with st.sidebar:
    st.header("Aircraft Tail Number to Track")
    tail_number = st.text_input("Enter Tail Number:", placeholder="e.g., N564PU") #tailnumber of old Purdue 14 aircraft



#function to get flight info from api. this function was a collaboration between the student and ChatGPT.
def fetch_flight_info(callsign):
    if not callsign:
        return None
    try:
        #GET request to the OpenSky API
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        #filter results
        flights = data.get("states", [])
        for flight in flights:
            if flight[1] and callsign.upper() in flight[1].strip():
                velocity_in_mps = flight[9]  # Velocity is at index 9
                velocity_in_knots = velocity_in_mps * 1.94384 if velocity_in_mps else None
                altitude_in_meters = flight[13]  # Altitude is at index 13
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
        st.error(f"Error fetching data from OpenSky API: {e}")
        return None

#fetchs information. this function was a collaboration between the student and ChatGPT.
if tail_number:
    info = fetch_flight_info(tail_number)
    if info:
        # Display aircraft info in the sidebar
        st.sidebar.subheader("Aircraft Information")
        st.sidebar.write(f"**Callsign:** {info['callsign']}")
        st.sidebar.write(f"**Origin Country:** {info['origin_country']}")
        #st.sidebar.write(f"**Velocity:** {info['velocity']} m/s") #removed after conversion to knots of airspeed
        #st.sidebar.write(f"**Altitude:** {info['altitude']:.2f} feet") #removed after conversion from meters to feet

        #displays airspeed
        if info["velocity_knots"] is not None:
            st.sidebar.write(f"**Airspeed:** {info['velocity_knots']:.2f} knots")
        else:
            st.sidebar.write("**Airspeed:** Data not available")

        #checks if altitude is available before displaying it
        if info["altitude_feet"] is not None:
            st.sidebar.write(f"**Altitude:** {info['altitude_feet']:.2f} feet")
        else:
            st.sidebar.write("**Altitude:** Data not available")
        
        #checks if heading is available before displaying it
        if info["heading"] is not None:
            st.sidebar.write(f"**Heading:** {info['heading']:.2f}°")
        else:
            st.sidebar.write("**Heading:** Data not available")


        #adds plane marker on the map
        if info["latitude"] and info["longitude"]:
            folium.Marker(
                location=[info["latitude"], info["longitude"]],
                #adds popup with same info below tail number entry
                popup=(
                    f"Callsign: {info['callsign']}\n"
                    f"Origin Country: {info['origin_country']}\n"
                    f"Airspeed: {info['velocity_knots']:.2f} knots\n"
                    f"Altitude: {info['altitude_feet']:.2f} feet\n"
                    f"Heading: {info['heading']:.2f}°"
                ),
                icon=folium.Icon(color="blue", icon="plane"),
            ).add_to(m)
        else:
            st.warning("Location data not available for this flight.")
    else:
        st.warning("No flight information found for the provided tail number.")

#displays map
st_folium(m, width=700, height=500)
