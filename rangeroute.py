'''
rangeroute.py

Finds the shortest route between two airports such that each leg is within
the maximum range of one's aircraft.

'''

import sys
from rich.console import Console
from rich.table import Column, Table, box
from rich.markdown import Markdown
from rich.progress import track

from igrf.magvar import Magvar
from utils import db, globenav

console = Console()

MV = Magvar()

def distance(a,b):
    aLat = float(a['latitude_deg'])
    aLon = float(a['longitude_deg'])
    bLat = float(b['latitude_deg'])
    bLon = float(b['longitude_deg'])
    return globenav.dist_coord(aLat, aLon, bLat, bLon)

# bearing from A -> B
def bearing(a,b):
    aLat = float(a['latitude_deg'])
    aLon = float(a['longitude_deg'])
    bLat = float(b['latitude_deg'])
    bLon = float(b['longitude_deg'])
    midLat = (aLat + bLat) / 2
    midLon = (aLon + bLon) / 2
    return globenav.wrap_brg(globenav.brg_coord(aLat, aLon, bLat, bLon) - MV.declination(midLat, midLon, 0))

if len(sys.argv) > 2:
    src = sys.argv[1].upper()
    dst = sys.argv[2].upper()

    if src == dst:
        sys.exit("Your source and destination are the same!")

    if len(sys.argv) > 3:
        try:
            maxRange = float(sys.argv[3])
        except TypeError:
            sys.exit("You must provide a numeric maxium range!")
    else:
        sys.exit("You must provide a maximum range!")
else:
    sys.exit("You must provide two ICAO airport codes and a maximum range!")

possibleSources=[]
possibleDests=[]

Q = []
dist = {}
prev = {}

def matchICAOCodesAndPrep(element):
    ident = element['ident']
    if ident == src:
        possibleSources.append(element)
    elif ident == dst:
        possibleDests.append(element)
    element['dist'] = 99999
    element['prev'] = None
    Q.append(element)

db.execute('airports.csv', matchICAOCodesAndPrep)

if len(possibleSources) == 0 or len(possibleDests) == 0:
    if len(possibleSources) == 0:
        print("Can't find " + src + "!")
    if len(possibleDests) == 0:
        print("Can't find " + dst + "!")
    sys.exit()

refSource = None
refDest = None

refSource = possibleSources[0]
region = possibleSources[0]['iso_country']
anyRegion = False

def minSortdist(e):
    return e['sortdist']

for dest in possibleDests:
    dest['sortdist'] = distance(refSource,dest)
possibleDests.sort(key=minSortdist)
refDest = possibleDests[0]

srcName = refSource['name']
dstName = refDest['name']
srcLat = float(refSource['latitude_deg'])
srcLong = float(refSource['longitude_deg'])
dstLat = float(refDest['latitude_deg'])
dstLong = float(refDest['longitude_deg'])

refSource['dist'] = 0

basic       = ['closed', 'seaplane_base']
smallAp    = ['small_airport']
mediumAp    = ['medium_airport']
largeAp     = ['large_airport']
# Large Airports only by default
filterTypes = basic + smallAp + mediumAp

print("")
print("Enter number of airport filter (or press Return for 1):\n")
print("  [1] - Large airports only")
print("  [2] - Medium airports only")
print("  [3] - Small airports only")
print("  [4] - Large and medium airports")
print("  [5] - Small and medium airports")
print("  [6] - All airports (very slow)")

print("")
routeSelect = input("> ").rstrip()
if routeSelect == "2":
    filterTypes = basic + smallAp + largeAp
elif routeSelect == "3":
    filterTypes = basic + mediumAp + largeAp
elif routeSelect == "4":
    filterTypes = basic + smallAp
elif routeSelect == "5":
    filterTypes = basic + largeAp
elif routeSelect == "6":
    filterTypes = basic

extremeDist = globenav.dist_coord(srcLat,srcLong,dstLat,dstLong)
midLat = (srcLat+dstLat)/2
midLon = (srcLong + dstLong)/2

# Eliminate heliports or airports that are wildly out of range
Z = []
while Q:
    e = Q.pop()
    allow = True
    eLat = float(e['latitude_deg'])
    eLon = float(e['longitude_deg'])
    if globenav.dist_coord(midLat,midLon,eLat,eLon) > extremeDist:
        allow=False
    else:
        eType = e['type'].rstrip()
        for fType in filterTypes:
            if eType == fType:
                allow=False
                break
    if allow and e['type'].find("heli") == -1:
        Z.append(e)

Q = Z

print("\nPlease wait... considering " + str(len(Q)) + " possible airports.\n")

def min_dist(e):
    return e['dist']

while len(Q) > 0:
    Q.sort(key=min_dist)
    u = Q.pop(0)

    if u==refDest:
        break

    uLat = float(u['latitude_deg'])
    uLon = float(u['longitude_deg'])
    for v in Q:
        vLat = float(v['latitude_deg'])
        vLon = float(v['longitude_deg'])
        nodeDist = globenav.dist_coord(uLat,uLon,vLat,vLon)
        # consider v a neighbor of u if u within max range
        if nodeDist <= maxRange:
            alt = u['dist'] + nodeDist
            if alt < v['dist']:
                v['dist'] = alt
                v['prev'] = u

S = []
u = refDest
if u['prev'] != None or u == refSource:
    while not (u == None):
        S.insert(0, u)
        u = u['prev']

if len(S) == 0:
    sys.exit("Can't find a valid route! Try searching more airports, or use a larger maximum range.\n")

# remove source and destination
S.remove(S[0])
S.remove(S[len(S)-1])

naTable = Table(show_header=True, box=box.SIMPLE)
naTable.add_column("Leg #", justify="center")
naTable.add_column("ID", justify="center")
naTable.add_column("Name", justify="left")
naTable.add_column("Distance", justify="right")
naTable.add_column("Heading", justify="right")
prevNode = refSource
totalDist = 0
naTable.add_row("", refSource['ident'], refSource['name'], "", "")
for i in range(len(S)):
    navaid = S[i]
    nDist = distance(prevNode, navaid)
    nBrg = int(round(bearing(prevNode, navaid)))
    naTable.add_row(str(i+1), navaid['ident'], navaid['name'], str(round(nDist,1)) + " nm", str(nBrg) + "°")
    prevNode = navaid
    totalDist += nDist

nDist = distance(prevNode, refDest)
totalDist += nDist
brgStr = ""
if nDist > 0.5:
    brgStr = str(int(round(bearing(prevNode, refDest)))) + "°"
naTable.add_row(str(len(S)+1), refDest['ident'], refDest['name'], str(round(distance(prevNode, refDest),1)) + " nm", brgStr)

print("")
console.print(Markdown("# Route from " + src + " (" + srcName + ") to " + dst + " (" + dstName + "), max leg distance of " + str(maxRange) + " nm"))
console.print(naTable)
console.print("[b]Total distance:[/b] " + str(int(round(totalDist))) + " nm")
print("")
routeStr = refSource['ident']
print("Route string for flight plan:")
for na in S:
    routeStr = routeStr + " " + na['ident']
routeStr = routeStr + " " + refDest['ident']
print(routeStr)
print("")