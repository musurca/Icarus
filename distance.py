'''
distance.py

Calculates the direct distance between two airport/navaids.

'''

import csv
import sys
from math import sin, cos, sqrt, atan2, radians, degrees

from igrf.magvar import Magvar

DATA_DIR = "./data/"

MV = Magvar()

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

def wrap_brg(b):
    if b < 0:
        b = 360+b
    elif b >= 360:
        b = 360-b
    return b

def brg_coord(lat1,lon1,lat2,lon2):
    # source: https://www.movable-type.co.uk/scripts/latlong.html
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    deltaLon = lon2 - lon1
    y = sin(deltaLon) * cos(lat2)
    x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(deltaLon)
    return wrap_brg(degrees(atan2(y, x)))

if len(sys.argv) > 2:
    src = sys.argv[1].upper()
    dst = sys.argv[2].upper()

    if src == dst:
        sys.exit("Your source and destination are the same!")

    if len(sys.argv) > 3:
        region = sys.argv[3].upper()
        anyRegion = False
    else:
        region = ""
        anyRegion = True
else:
    sys.exit("You must provide two ICAO airport/navaid codes and an (optional) region code!")

possibleSources=[]
possibleDests=[]

with open(DATA_DIR+'airports.csv', newline='') as csvfile:
    airports = csv.DictReader(csvfile)
    for airport in airports:
        ident = airport['ident']
        if ident == src:
            possibleSources.append(airport)
        elif ident == dst:
            possibleDests.append(airport)

with open(DATA_DIR+'navaids.csv', newline='') as csvfile:
    navaids = csv.DictReader(csvfile)
    for navaid in navaids:
        ident = navaid['ident']
        if ident == src:
            possibleSources.append(navaid)
        elif ident == dst:
            possibleDests.append(navaid)

if len(possibleSources) == 0 or len(possibleDests) == 0:
    if len(possibleSources) == 0:
        print("Can't find " + src + "!")
    if len(possibleDests) == 0:
        print("Can't find " + dst + "!")
    sys.exit()

refSource = None
refDest = None

if len(possibleSources) > 1:
    for source in possibleSources:
        country = source['iso_country']
        if anyRegion or region==country:
            refSource = source
            region = country
            anyRegion = False
            break
    if refSource == None:
        refSource = possibleSources[0]
        region = possibleSources[0]['iso_country']
        anyRegion = False
else:
    refSource = possibleSources[0]
    region = possibleSources[0]['iso_country']
    anyRegion = False

if len(possibleDests) > 1:
    for dest in possibleDests:
        country = dest['iso_country']
        if region==country:
            refDest = dest
            break
    if refDest == None:
        refDest = possibleDests[0]
else:
    refDest = possibleDests[0]

srcLat = float(refSource['latitude_deg'])
srcLong = float(refSource['longitude_deg'])
srcName = refSource['name']
dstLat = float(refDest['latitude_deg'])
dstLong = float(refDest['longitude_deg'])
dstName = refDest['name']

dist = dist_coord(srcLat,srcLong,dstLat,dstLong)
brg = wrap_brg(brg_coord(srcLat, srcLong, dstLat, dstLong) - MV.declination((dstLat+srcLat)/2,(dstLong+srcLong)/2,0))

print(src + " (" + srcName + ") --> " + dst + " (" + dstName + ")")
print(str(round(dist,1)) + " nm @ " + str(int(round(brg)))+"°")