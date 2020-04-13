'''
airportinfo.py

Displays relevant information about an airport: radio frequencies, runways, etc.

'''

import csv
import sys

from math import sin, cos, sqrt, atan2, radians

DATA_DIR = "./data/"

# distance between two global points in nautical miles
def dist_coord(lat1,lon1,lat2,lon2): 
    # source: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude  
    R = 6373.0 # approximate radius of earth in km
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return 0.539957*R * c

if len(sys.argv) > 1:
    code = sys.argv[1].upper()
else:
    sys.exit("You must provide an ICAO airport code!")

apName = None
# get basic info
with open(DATA_DIR+'airports.csv', newline='') as csvfile:
    airports = csv.DictReader(csvfile)
    for airport in airports:
        ident = airport['ident']
        if ident == code:
            apLat = float(airport['latitude_deg'])
            apLong = float(airport['longitude_deg'])
            apName = airport['name']
            apId = airport['id']
            apElev = airport['elevation_ft']
            break

if apName == None:
    sys.exit("Can't find airport " + code + "!")

print("")
print(apName + " (" + code + ")")
if apLat >= 0:
    latText = str(round(abs(apLat),6)) + "°N"
else:
    latText = str(round(abs(apLat),6)) + "°S"
if apLong >= 0:
    longText = str(round(abs(apLong),6)) + "°E"
else:
    longText = str(round(abs(apLong),6)) + "°W"
print(latText + ", " + longText + ", elev. " + apElev + " ft ASL")
print("------------------------------------------------------")

# runways
with open(DATA_DIR+'runways.csv', newline='') as csvfile:
    runways = csv.DictReader(csvfile)
    for runway in runways:
        refId = runway['airport_ident']
        if refId == code and runway['closed'] == "0":
            if runway['le_ident'][0:1] == "H":
                print("Helipad " + runway['le_ident'] + " -- " + runway['length_ft'] + " ft")
            else:
                print("Runway " + runway['le_ident'] + " (" + runway['le_heading_degT'] + "°) / " + runway['he_ident'] + " (" + runway['he_heading_degT'] + "°) -- " + runway['length_ft'] + " ft")

# navaids
print("")
with open(DATA_DIR+'navaids.csv', newline='') as csvfile:
    navaids = csv.DictReader(csvfile)
    for navaid in navaids:
        refId = navaid['associated_airport']
        if refId == code:
            navLat = float(navaid['latitude_deg'])
            navLong = float(navaid['longitude_deg'])
            dist = dist_coord(apLat, apLong, navLat, navLong)
            if navaid['frequency_khz'] != "":
                if navaid['type'] == "NDB":
                    freq = navaid['frequency_khz'] + " mHz"
                else:
                    freq = str(float(navaid['frequency_khz'])/1000) + " mHz"
            else:
                freq = ""
            print(navaid['ident'] + " (" + navaid['name'] + " " + navaid['type'] + ") @ " + freq + " -- " + str(round(dist,2)) + " nm")

# com frequencies
print("")
with open(DATA_DIR+'airport-frequencies.csv', newline='') as csvfile:
    freqs = csv.DictReader(csvfile)
    for freq in freqs:
        refId = freq['airport_ident']
        if refId == code:
            print(freq['type'] + "\t" + freq['frequency_mhz'] + " mHz\t(" + freq['description'] + ")")


print("")