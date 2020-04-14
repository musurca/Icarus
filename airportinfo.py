'''
airportinfo.py

Displays relevant information about an airport: radio frequencies, runways, etc.

TODO: customize radius of nearby airports
TODO: find magnetic deviation
TODO: if you can't find the airport code, try putting a 'K' in front of it
TODO: if you can't find the airport code and it's 4-letters long, try removing the first letter
TODO: maybe make this into a general info utility that also works on navaids
TODO: handle hybrid runway materials (or maybe just get entire list of possibilites and classify)

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

def minDist(e):
    return e['dist']

def minLength(e):
    return e['length']

if len(sys.argv) > 1:
    code = sys.argv[1].upper()
else:
    sys.exit("You must provide an ICAO airport code!")

showHelipads = False
if len(sys.argv) > 2:
    if sys.argv[2] == "heli":
        showHelipads = True

apName = None
# find airport info
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
            if airport['type'].find("heli") != -1:
                showHelipads = True
            break

if apName == None:
    sys.exit("Can't find airport " + code + "!")

print("")
print(apName + " (" + code + ")")
if apLat >= 0:
    latDir = "°N"
else:
    latDir = "°S"
if apLong >= 0:
    longDir = "°E"
else:
    longDir = "°W"
latText = str(round(abs(apLat),6)) + latDir
longText = str(round(abs(apLong),6)) + longDir
print(latText + ", " + longText + ", elev. " + apElev + " ft ASL")
print("------------------------------------------------------")

# runways
runwayList = []
with open(DATA_DIR+'runways.csv', newline='') as csvfile:
    runways = csv.DictReader(csvfile)
    for runway in runways:
        refId = runway['airport_ident']
        if refId == code and runway['closed'] == "0":
            runway['length'] = int(runway['length_ft'])
            runwayList.append(runway)

# returns material of the runway
def runwayMaterial(rwy):
    # no common vocab for this so we have to be a bit flexible
    surf = rwy['surface'].upper()
    if surf.find("CON") != -1:
        return "concrete"
    elif surf.find("ASP") != -1:
        return "asphalt"
    elif surf.find("TUR") != -1:
        return "astroturf"
    elif surf.find("DIRT") != -1:
        return "dirt"
    elif surf.find("GRV") != -1 or surf.find("GRAV") != -1:
        return "gravel"
    elif surf.find("SAND") != -1:
        return "sand"
    elif surf.find("WAT") != -1:
        return "water"
    elif surf.find("MAT") != -1:
        return "mat"
    elif surf.find("GRASS") != -1:
        return "grass"
    else:
        return ""


runwayList.sort(key=minLength)
for runway in runwayList:
    rmat = runwayMaterial(runway)
    if len(rmat) > 0:
        matStr = ", " + rmat
    else:
        matStr = ""

    if len(runway['le_heading_degT']) > 0:
        leHeadingStr = " (" + runway['le_heading_degT'] + "°)"
    else:
        leHeadingStr = ""
    
    if len(runway['he_heading_degT']) > 0:
        heHeadingStr = " (" + runway['he_heading_degT'] + "°)"
    else:
        heHeadingStr = ""

    if runway['le_ident'][0:1] == "H":
        print("Helipad " + runway['le_ident'] + " -- " + runway['length_ft'] + " ft" + matStr)
    else:
        print("Runway " + runway['le_ident'] + leHeadingStr + " / " + runway['he_ident'] + heHeadingStr  + " -- " + runway['length_ft'] + " ft" + matStr)

# com frequencies
nearbyComFreqs=[]
with open(DATA_DIR+'airport-frequencies.csv', newline='') as csvfile:
    freqs = csv.DictReader(csvfile)
    for freq in freqs:
        refId = freq['airport_ident']
        if refId == code:
            nearbyComFreqs.append(freq)

if len(nearbyComFreqs) > 0:
    print("")
    for freq in nearbyComFreqs:
        print(freq['type'] + "\t" + freq['frequency_mhz'] + " mHz\t(" + freq['description'] + ")")

# show 5 closest navaids within 30nm
closenavaids=[]
with open(DATA_DIR+'navaids.csv', newline='') as csvfile:
    navaids = csv.DictReader(csvfile)
    for navaid in navaids:
        navLat = float(navaid['latitude_deg'])
        navLong = float(navaid['longitude_deg'])
        dist = dist_coord(apLat, apLong, navLat, navLong)
        if dist <= 30:
            navaid['dist'] = dist
            closenavaids.append(navaid)

closenavaids.sort(key=minDist)
if len(closenavaids) > 0:
    print("")
    for k in range(min(len(closenavaids),5)):
        navaid = closenavaids[k]
        if navaid['frequency_khz'] != "":
            if navaid['type'] == "NDB":
                freq = " @ " + navaid['frequency_khz'] + " mHz"
            else:
                freq = " @ " + str(float(navaid['frequency_khz'])/1000) + " mHz"
        else:
            freq = ""
        print(str(round(navaid['dist'],2)) + " nm:\t" + navaid['ident'] + " (" + navaid['name'] + " " + navaid['type'] + ")" + freq)

nearbyAirports = []
# find airports within 20nm
with open(DATA_DIR+'airports.csv', newline='') as csvfile:
    airports = csv.DictReader(csvfile)
    for airport in airports:
        ident = airport['ident']
        aLat = float(airport['latitude_deg'])
        aLong = float(airport['longitude_deg'])
        dist = dist_coord(apLat, apLong, aLat, aLong)
        if ident != code and dist <= 20 and (showHelipads or airport['type'].find("airport") != -1):
            airport['dist'] = dist
            nearbyAirports.append(airport)

nearbyAirports.sort(key=minDist)
if len(nearbyAirports) > 0:
    codeString = nearbyAirports[0]['ident']
    for k in range(len(nearbyAirports)-1):
        codeString = codeString + ", " + nearbyAirports[k+1]['ident']
    print("\nWithin 20nm: " + codeString)

print("")