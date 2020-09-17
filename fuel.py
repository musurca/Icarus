'''
fuel.py

Scrapes 100ll.com for avgas prices near an airport.

TODO: gets weird in Alaska. 
TODO: if you get only 1 FBO, include it
TODO: convert true headings to magnetic

'''
import sys

from rich.console import Console
from rich.table import Column, Table, box
from rich.markdown import Markdown

from utils import scrape, db

console = Console()

if len(sys.argv) > 1:
    airportCode = sys.argv[1].upper()
    if len(airportCode) != 4:
        sys.exit("You must provide a four-letter ICAO code!")
else:
    sys.exit("You must provide an airport ICAO code!")

maxDist = 30
if len(sys.argv) > 2:
    if sys.argv[2].isnumeric():
        maxDist = int(sys.argv[2])
    else:
        sys.exit("Error reading max distance!")

jetFuel = False
if len(sys.argv) > 3:
    if sys.argv[3].upper() == "JETA":
        jetFuel = True

s = scrape.getSession()
fbo_soup = scrape.getSoup(s, 'http://www.100ll.com/searchresults.php?clear_previous=true&searchfor=' + airportCode + '&submit.x=0&submit.y=0')

# First, find a valid FBO hash ID near our airport
scrapeArg = ""
for tr in fbo_soup.find_all('tr'):
    if tr.has_attr('id'):
        if str(tr['id']).find("fbo_") != -1:
            if tr.has_attr('onclick'):
                clickStr = str(tr['onclick'])
                scrapeArg = clickStr[29:len(clickStr)-1]
                break

if scrapeArg == "":
    # we got a single FBO instead of a list, so find a link
    # to the hashID of this one and check nearest
    for a in fbo_soup.find_all('a'):
        if a.has_attr('href'):
            hrefStr = str(a['href'])
            if hrefStr.find("?HashID") != -1:
                scrapeArg = hrefStr[hrefStr.find("?")+1:]

# Plug in HashID and scrape nearby FBOs and their prices
fuelSearchType = "fuel"
fuelType = "100LL"
if jetFuel == True:
    fuelType = "JET-A"
    fuelSearchType = "jeta"

soup = scrape.getSoup(s, 'http://www.100ll.com/shownearby' + fuelSearchType + '.php?' + scrapeArg)
fboTable=[]
for tr in soup.find_all('tr'):
    if tr.has_attr('id'):
        if str(tr['id']).find("fbo_") != -1:
            tab = tr.find_all('td')
            if len(tab) >= 7:
                distanceStr=tab[6].string
                dist=distanceStr[:distanceStr.find("NM")]
                direction=distanceStr[distanceStr.find("@")+2:]
                fboTable.append({'airport':tab[1].string, 'fbo_name':tab[2].string, 'self':tab[3].string, 'full':tab[4].string, 'update':tab[5].string, 'dist':int(dist), 'direction':direction})

if len(fboTable) == 0:
    sys.exit("No fuel sources found near " + airportCode + ".")

# sort FBOs by distance from airport
fboTable.sort(key=db.sortKeyMinDist)

print("")
console.print(Markdown("### " + fuelType + " PRICES @ " + airportCode))
localFuelTable = Table(show_header=True, box=box.SIMPLE)
localFuelTable.add_column("Self")
localFuelTable.add_column("Full")
localFuelTable.add_column("FBO")
for fbo in fboTable:
    if fbo['airport'] == airportCode or fbo['dist'] == 0:
        localFuelTable.add_row(fbo['self'],fbo['full'],fbo['fbo_name'])
console.print(localFuelTable)

print("")
console.print(Markdown("### " + fuelType + " PRICES NEARBY"))
fuelTable = Table(show_header=True, box=box.SIMPLE)
fuelTable.add_column("ID")
fuelTable.add_column("Self")
fuelTable.add_column("Full")
fuelTable.add_column("Distance")
fuelTable.add_column("Direction")
fuelTable.add_column("FBO")
for fbo in fboTable:
    if fbo['airport'] != airportCode and fbo['dist'] <= maxDist:
        fuelTable.add_row(fbo['airport'],fbo['self'],fbo['full'],str(fbo['dist']) + " nm",fbo['direction'],fbo['fbo_name'])
console.print(fuelTable)
print("")