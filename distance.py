'''
distance.py

Calculates the direct distance between two airport/navaids.

'''

import sys
from rich.console import Console
from rich.markdown import Markdown

from igrf.magvar import Magvar
from utils import db, globenav

console = Console()

MV = Magvar()

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

def matchICAOCodes(element):
    ident = element['ident']
    if ident == src:
        possibleSources.append(element)
    elif ident == dst:
        possibleDests.append(element)

db.execute('airports.csv', matchICAOCodes)
db.execute('navaids.csv', matchICAOCodes)

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

def distance(a,b):
    aLat = float(a['latitude_deg'])
    aLon = float(a['longitude_deg'])
    bLat = float(b['latitude_deg'])
    bLon = float(b['longitude_deg'])
    return globenav.dist_coord(aLat, aLon, bLat, bLon)

for dest in possibleDests:
    dest['dist'] = distance(refSource,dest)
# sort by smallest -> largest distance and select smallest
possibleDests.sort(key=lambda e:e['dist'])
refDest = possibleDests[0]

srcLat = float(refSource['latitude_deg'])
srcLong = float(refSource['longitude_deg'])
srcName = refSource['name']
dstLat = float(refDest['latitude_deg'])
dstLong = float(refDest['longitude_deg'])
dstName = refDest['name']

src = refSource['ident']
dst = refDest['ident']

dist = globenav.dist_coord(srcLat,srcLong,dstLat,dstLong)

# account for magnetic declination at midpoint between navigation points
brg = globenav.wrap_brg(globenav.brg_coord(srcLat, srcLong, dstLat, dstLong) - MV.declination((dstLat+srcLat)/2,(dstLong+srcLong)/2,0))

print("")
console.print(Markdown("# " + src + " (" + srcName + ") --> " + dst + " (" + dstName + ")"))
print("")
console.print(Markdown("### " + (str(round(dist,1)) + " nm @ " + str(int(round(brg)))+"°")))
print("")