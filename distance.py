'''
distance.py

Calculates the direct distance between two airports.

TODO: support navaids as well

'''

import csv
import sys

from math import sin, cos, sqrt, atan2, radians

DATA_DIR = "./data/"

if len(sys.argv) > 2:
    src = sys.argv[1].upper()
    dst = sys.argv[2].upper()
    if len(sys.argv) > 3:
        region = sys.argv[3].upper()
        anyRegion = False
    else:
        region = ""
        anyRegion = True
else:
    sys.exit("You must provide two ICAO airport/navaid codes and an (optional) region code!")

srcLat = None
dstLat = None

# try airports first
with open(DATA_DIR+'airports.csv', newline='') as csvfile:
    airports = csv.DictReader(csvfile)
    for airport in airports:
        ident = airport['ident']
        country = airport['iso_country']
        if ident == src and (anyRegion or region==country):
            srcLat = float(airport['latitude_deg'])
            srcLong = float(airport['longitude_deg'])
            srcName = airport['name']
        elif ident == dst and (anyRegion or region==country):
            dstLat = float(airport['latitude_deg'])
            dstLong = float(airport['longitude_deg'])
            dstName = airport['name']

# if we don't have enough data, try navaids next
if srcLat == None or dstLat == None:
    with open(DATA_DIR+'navaids.csv', newline='') as csvfile:
        navaids = csv.DictReader(csvfile)
        for navaid in navaids:
            ident = navaid['ident']
            country = navaid['iso_country']
            if ident == src and (anyRegion or region==country):
                srcLat = float(navaid['latitude_deg'])
                srcLong = float(navaid['longitude_deg'])
                srcName = navaid['name']
            elif ident == dst and (anyRegion or region==country):
                dstLat = float(navaid['latitude_deg'])
                dstLong = float(navaid['longitude_deg'])
                dstName = navaid['name']

if srcLat == None or dstLat == None:
    if srcLat == None:
        print("Can't find " + src + "!")
    if dstLat == None:
        print("Can't find " + dst + "!")
    sys.exit()

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

dist = dist_coord(srcLat,srcLong,dstLat,dstLong)

print(src + " (" + srcName + ") --> " + dst + " (" + dstName + ")")
print(str(round(dist,2)) + " nm")