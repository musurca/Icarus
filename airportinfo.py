'''
airportinfo.py

Displays relevant information about an airport: radio frequencies, runways, etc.

TODO: customize radius of nearby airports
TODO: if you can't find the airport code, try putting a 'K' in front of it
TODO: if you can't find the airport code and it's 4-letters long, try removing the first letter
TODO: maybe make this into a general info utility that also works on navaids
TODO: handle hybrid runway materials (or maybe just get entire list of possibilites and classify)

'''
import requests
import sys
from math import sin, cos, sqrt, atan2, radians, degrees

from bs4 import BeautifulSoup

from igrf.magvar import Magvar

from utils import db, runwayMaterial, decode_remark, globenav, longestSubstringFinder

CHART_SOURCE = 'https://nfdc.faa.gov/nfdcApps/services/ajv5/airportDisplay.jsp?airportId='

MV = Magvar()

def minDist(e):
    return e['dist']

if len(sys.argv) > 1:
    code = sys.argv[1].upper()
else:
    sys.exit("You must provide an ICAO airport code!")

showHelipads = False
if len(sys.argv) > 2:
    if sys.argv[2] == "heli":
        showHelipads = True

# QUERY - find airport by provided ICAO code
airport = None

# check updated list of airports
def airportMatchesICAO(airport):
    return airport['ident'] == code

mod_airport = db.findFirst('airports.csv', airportMatchesICAO)

# check archaic FSX/FSE list of airports
def fseAirportMatchesICAO(airport):
    return airport['icao'] == code

fse_airport = db.findFirst('fse/icaodata.csv', fseAirportMatchesICAO)

def closestModernAirports(airport):
        lat = float(airport['latitude_deg'])
        lon = float(airport['longitude_deg'])
        dist = globenav.dist_coord(fseLat, fseLong, lat, lon)
        return dist <= 100, dist

def closestProcess(airport, args):
        airport['dist'] = args[0]

if mod_airport != None:    
    if fse_airport != None:
        modLat = float(mod_airport['latitude_deg'])
        modLong = float(mod_airport['longitude_deg'])
        fseLat = float(fse_airport['lat'])
        fseLong = float(fse_airport['lon'])
        dist = globenav.dist_coord(modLat, modLong, fseLat, fseLong)
        if dist <= 2:
            # Entries are within 2nm, close enough for gov't work, move on
            airport = mod_airport
        else:
            # Discrepancy -- we got some 'splainin to do!
            fseLat = float(fse_airport['lat'])
            fseLong = float(fse_airport['lon'])

            curFseAirports = db.query('airports.csv', closestModernAirports, closestProcess)
            curFseAirports.sort(key=minDist)

            if len(curFseAirports) == 0:
                # We can't solve this, so err on the side of the modern airport
                airport = mod_airport
            else:
                for airport in curFseAirports:
                    substr = longestSubstringFinder(airport['name'], fse_airport['name'])
                    airport['nameMatchLen'] = len(substr)
                
                def minSublen(e):
                    return e['nameMatchLen']
                curFseAirports.sort(key=minSublen)

                curFseAirport = curFseAirports[len(curFseAirports)-1]

                print("Did you mean " + mod_airport['name'] + " (" + mod_airport['ident'] + "), or " + curFseAirport['name'] + " (" + curFseAirport['ident'] + " — formerly " + code + ")?")
                newCode = input("Enter current ICAO code (or press Return for " + code + "): ").rstrip().upper()
                if (not newCode) or newCode != curFseAirport['ident']:
                    airport = mod_airport
                else:
                    airport = curFseAirport
    else:
        airport = mod_airport
else:
    if fse_airport != None:
        fseLat = float(fse_airport['lat'])
        fseLong = float(fse_airport['lon'])

        mod_airports = db.query('airports.csv', closestModernAirports, closestProcess)
        mod_airports.sort(key=minDist)

        if len(mod_airports) > 0:
            airport = mod_airports[0]

if airport != None:
    apLat = float(airport['latitude_deg'])
    apLong = float(airport['longitude_deg'])
    apName = airport['name']
    apId = airport['id']
    apElev = airport['elevation_ft']
    apType = airport['type']
    if airport['type'].find("heli") != -1:
        showHelipads = True
else:
    sys.exit("Can't find airport " + code + "!")

code = airport['ident']

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

# QUERY - find closest city within 20nm
def isCityWithin20NM(city):
    cLat = float(city['lat'])
    cLong = float(city['lng'])
    cDist = globenav.dist_coord(apLat, apLong, cLat, cLong)
    return (cDist < 20, cDist)

def cityProcess(city, args):
    city['dist'] = args[0]

cityList = db.query('/cities/uscities.csv', isCityWithin20NM, cityProcess)

def minPopulation(e):
    return float(e['population'])

# choose city at shortest distance if a small airport or heliport, 
# or with largest population if it's medium/large
if len(cityList) > 0:
    if apType.find("small") != -1 or apType.find("heli") != -1:
        cityList.sort(key=minDist)
        city = cityList[0]
    else:
        cityList.sort(key=minPopulation)
        city = cityList[len(cityList)-1]
    print("Closest city: " + city['city_ascii'] + ", " + city['state_id'] + " (" + str(round(city['dist'],1)) + "nm)")

print("------------------------------------------------------")      

# QUERY - airport runways
def minLength(e):
    return e['length']

def openAndMatchesICAO(runway):
    refId = runway['airport_ident']
    return refId == code and runway['closed'] == "0",

def runwayProcess(runway, args):
    runway['length'] = int(runway['length_ft'])

runwayList = db.query('runways.csv', openAndMatchesICAO, runwayProcess)
runwayList.sort(key=minLength)

for runway in runwayList:
    rmat = runwayMaterial(runway['surface'])
    if len(rmat) > 0:
        matStr = ", " + rmat
    else:
        matStr = ""

    if runway['lighted'] == '1':
        matStr = matStr + " (L)"

    if len(runway['le_heading_degT']) > 0:
        leHeadingStr = " (" + str(int(round(float(runway['le_heading_degT'])))) + "°)"
    else:
        leHeadingStr = ""
    
    if len(runway['he_heading_degT']) > 0:
        heHeadingStr = " (" + str(int(round(float(runway['he_heading_degT'])))) + "°)"
    else:
        heHeadingStr = ""

    if runway['le_ident'][0:1] == "H":
        print("Helipad " + runway['le_ident'] + " -- " + runway['length_ft'] + " ft" + matStr)
    else:
        print("Runway " + runway['le_ident'] + leHeadingStr + " / " + runway['he_ident'] + heHeadingStr  + " -- " + runway['length_ft'] + " ft" + matStr)

# QUERY -- airport com frequencies
def matchesICAOCode(freq):
    return freq['airport_ident'] == code,

nearbyComFreqs = db.query('airport-frequencies.csv', matchesICAOCode)

if len(nearbyComFreqs) > 0:
    print("")
    for freq in nearbyComFreqs:
        print(freq['type'] + "\t" + freq['frequency_mhz'] + " mHz\t(" + freq['description'] + ")")

# QUERY --  5 closest navaids to airport within 30nm

# filter by navaids within 50 nm
def isWithinRange(navaid):
    navLat = float(navaid['latitude_deg'])
    navLong = float(navaid['longitude_deg'])
    dist = globenav.dist_coord(apLat, apLong, navLat, navLong)
    return (dist<=50, dist, navLat, navLong)

# save distance and radial to airport
def navaidPostprocess(navaid, args):
    dist, navLat, navLong = args
    navaid['dist'] = dist
    navMagVar = MV.declination(navLat, navLong,0)
    brg = globenav.wrap_brg(globenav.brg_coord(navLat, navLong, apLat, apLong) - navMagVar)
    navaid['radial'] = str(int(round(brg)))

closenavaids = db.query('navaids.csv', isWithinRange, navaidPostprocess)
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
        print(str(round(navaid['dist'],1)) + " nm/rad " + navaid['radial'] + "°:\t" + navaid['ident'] + " (" + navaid['name'] + " " + navaid['type'] + ")" + freq)

# QUERY - other airports within 20nm
def airportFilter(airport):
    ident = airport['ident']
    aLat = float(airport['latitude_deg'])
    aLong = float(airport['longitude_deg'])
    dist = globenav.dist_coord(apLat, apLong, aLat, aLong)
    return (ident != code and dist <= 20 and (showHelipads or airport['type'].find("airport") != -1), dist)

def airportProcess(airport, args):
    airport['dist'] = args[0]

nearbyAirports = db.query('airports.csv', airportFilter, airportProcess)
nearbyAirports.sort(key=minDist)

if len(nearbyAirports) > 0:
    codeString = nearbyAirports[0]['ident']
    for k in range(len(nearbyAirports)-1):
        codeString = codeString + ", " + nearbyAirports[k+1]['ident']
    print("\nWithin 20nm: " + codeString)

# find & decode updated remarks
s = requests.Session() 
chart_soup = BeautifulSoup(s.get(CHART_SOURCE + code).text, features="html.parser")

remarks = []
for div in chart_soup.find_all('div'):
    if div.has_attr('id'):
        if div['id'].find("remarks") != -1:
            for remark in div.find_all('li'):
                remarks.append(decode_remark(remark.text).upper())

if len(remarks) > 0:
    print("")
    for remark in remarks:
        print("- " + remark)
print("")