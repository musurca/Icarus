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

    if len(src) != 4 or len(dst) != 4:
        sys.exit("You must provide four-letter ICAO codes!")
else:
    sys.exit("You must provide two four-letter airport ICAO codes!")

# load airports
with open(DATA_DIR+'airports.csv', newline='') as csvfile:
    airports = csv.DictReader(csvfile)
    for airport in airports:
        ident = airport['ident']
        if ident == src:
            srcLat = float(airport['latitude_deg'])
            srcLong = float(airport['longitude_deg'])
            srcName = airport['name']
        elif ident == dst:
            dstLat = float(airport['latitude_deg'])
            dstLong = float(airport['longitude_deg'])
            dstName = airport['name']

# distance between two global points in kilometers
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
    return R * c

# convert kilometers to nautical miles
def km_to_nm(n):
    return 0.539957*n

dist = dist_coord(srcLat,srcLong,dstLat,dstLong)

print(src + " (" + srcName + ") --> " + dst + " (" + dstName + ")")
print(str(round(km_to_nm(dist),2)) + " nm")