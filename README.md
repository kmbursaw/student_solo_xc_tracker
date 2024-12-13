# student_solo_xc_tracker
GEOG 576 Final Project

to run this program, you will need to download streamlit and folium.
  pip install streamlit folium requests
            or
  pip install streamlit[all]

to run this program in VS Code, open the terminal and type the following:
  streamlit run streamlit_test.py

First, pick your basemap. There are three choices. The third choice is best for night operations, or when you are in a dark room.

Second, type in the tailnumber of the aircraft you are searching for. For a student solo, usually the tail number will start with an N. If you want to just test to see any aircraft data, it is suggested that you go to this website, https://www.airnavradar.com/, click on an airplane, and type that tailnumber in. I would suggest using a well known airline airliner, and type in the tailnumber on the second line, (the one in light gray). An example tailnumber is also provided grayed out in the search container.

After hitting enter, if the tail number is found, then an airplane icon will pop up on the map, as well as information about the airplanes heading, altitude, and airspeed will be displayed below the searchbox. You can also click on the icon and have it bring up the same information in the map container. 


when finished with the program:
  Ctrl + C
