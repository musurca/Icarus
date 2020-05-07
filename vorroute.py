'''
vorroute.py

Finds the shortest VOR-to-VOR route between two airports or navaids.

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
        region = sys.argv[3].upper()
        anyRegion = False
    else:
        region = ""
        anyRegion = True
else:
    sys.exit("You must provide two ICAO airport/navaid codes and an (optional) region code!")

possibleSources=[]
possibleDests=[]

Q = []
dist = {}
prev = {}

def matchICAOCodes(element):
    ident = element['ident']
    if ident == src:
        possibleSources.append(element)
    elif ident == dst:
        possibleDests.append(element)

def matchICAOCodesAndPrep(element):
    ident = element['ident']
    if ident == src:
        possibleSources.append(element)
    elif ident == dst:
        possibleDests.append(element)
    element['dist'] = 99999
    element['prev'] = None
    Q.append(element)

db.execute('airports.csv', matchICAOCodes)
db.execute('navaids.csv', matchICAOCodesAndPrep)

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
if not (refSource in Q):
    refSource['prev'] = None
    Q.append(refSource)

if not (refDest in Q):
    refDest['dist'] = 99999
    refDest['prev'] = None
    Q.append(refDest)

maxDist = 2*globenav.dist_coord(srcLat,srcLong,dstLat,dstLong)
midLat = (srcLat+dstLat)/2
midLon = (srcLong + dstLong)/2

milTypes    = ['TACAN']
modNonMilTypes = ['VOR-DME', 'VOR']
modTypes    = ['VOR-DME', 'VORTAC','VOR']
legTypes    = ['NDB', 'NDB-DME']
# modern civilian by default
filterTypes = milTypes + legTypes

print("")
print("Enter number of VOR route type (or press Return for 1):\n")
print("  [1] - Modern civilian (VOR/DME only)")
print("  [2] - Legacy civilian (NDB only)")
print("  [3] - All civilian (VOR/DME & NDB)")
print("  [4] - Military (TACAN/VORTAC only)")
print("  [5] - All available ")

print("")
routeSelect = input("> ").rstrip()
if routeSelect == "2":
    filterTypes = modTypes + milTypes
elif routeSelect == "3":
    filterTypes = milTypes
elif routeSelect == "4":
    filterTypes = legTypes + modNonMilTypes
elif routeSelect == "5":
    filterTypes = []

# Eliminate unnecessary navaids
Z = []
while Q:
    e = Q.pop()
    eLat = float(e['latitude_deg'])
    eLon = float(e['longitude_deg'])
    allow = True
    if globenav.dist_coord(midLat,midLon,eLat,eLon) > maxDist:
        allow = False
    else:
        eType = e['type'].rstrip().upper()
        for fType in filterTypes:
            if eType == fType:
                allow=False
                break
        if allow:
            Z.append(e)

Q = Z

print("\nPlease wait... considering " + str(len(Q)) + " possible navaids.\n")

def min_dist(e):
    return e['dist']

VOR_ranges = { 'LOW':25, 'MEDIUM':40, 'HIGH':130, 'UNKNOWN':25, '':25 }
NDB_ranges = { 'LOW':25, 'MEDIUM':250, 'HIGH':500, 'UNKNOWN':15, '':15 }

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
        # consider v a neighbor of u if u within range of v's signal
        if 'power' in v:
            if v['type'] in legTypes:
                nodePower = NDB_ranges[v['power']]
            else:
                nodePower = VOR_ranges[v['power']]
        else:
            if v['type'] in legTypes:
                nodePower = NDB_ranges['LOW']
            else:
                nodePower = VOR_ranges['LOW']

        if nodeDist <= nodePower:
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
    sys.exit("Can't find a valid route! Try a more permissive route type (e.g. \"All civilian\" or \"All available\").\n")

# remove source and destination
S.remove(S[0])
S.remove(S[len(S)-1])

naTable = Table(show_header=True, box=box.SIMPLE)
naTable.add_column("#", justify="center")
naTable.add_column("ID", justify="center")
naTable.add_column("Name", justify="left")
naTable.add_column("Distance", justify="right")
naTable.add_column("Heading", justify="right")
naTable.add_column("Type", justify="left")
naTable.add_column("Freq (mHz)", justify="right")
prevNode = refSource
totalDist = 0
naTable.add_row("1", refSource['ident'], refSource['name'], "", "", "----", "----")
for i in range(len(S)):
    navaid = S[i]
    if navaid['frequency_khz'] != "":
        if navaid['type'] == "NDB":
            freq = navaid['frequency_khz']
        else:
            freq = str(float(navaid['frequency_khz'])/1000)
    else:
        freq = ""
    nDist = distance(prevNode, navaid)
    nBrg = int(round(bearing(prevNode, navaid)))
    naTable.add_row(str(i+2), navaid['ident'], navaid['name'], str(round(nDist,1)) + " nm", str(nBrg) + "°", navaid['type'], freq)
    prevNode = navaid
    totalDist += nDist

nDist = distance(prevNode, refDest)
totalDist += nDist
brgStr = ""
distStr = ""
if nDist > 0:
    brgStr = str(int(round(bearing(prevNode, refDest)))) + "°"
    distStr = str(round(nDist,1)) + " nm"
naTable.add_row(str(len(S)+2), refDest['ident'], refDest['name'], distStr, brgStr, "----", "----")

print("")
console.print(Markdown("# VOR-to-VOR Route from " + src + " (" + srcName + ") to " + dst + " (" + dstName + ")"))
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