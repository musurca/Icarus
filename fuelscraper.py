'''
fuelscraper.py

Scrapes 100ll.com for avgas prices near an airport.

TODO: gets weird in Alaska. 
TODO: if you get only 1 FBO, include it

'''
import requests
import sys
from bs4 import BeautifulSoup

def minDist(e):
    return e['dist']

if len(sys.argv) > 1:
    airportCode = sys.argv[1].upper()
    if len(airportCode) < 4:
        sys.exit("You must provide a four-letter ICAO code!")
else:
    sys.exit("You must provide an airport ICAO code!")

maxDist = 999
if len(sys.argv) > 2:
    if sys.argv[2].isnumeric():
        maxDist = int(sys.argv[2])
    else:
        sys.exit("Error reading max distance!")

s = requests.Session() 
fbo_soup = BeautifulSoup(s.get('http://www.100ll.com/searchresults.php?clear_previous=true&searchfor=' + airportCode + '&submit.x=0&submit.y=0').text, features="html.parser")

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
fuel_price_html = s.get('http://www.100ll.com/shownearbyfuel.php?' + scrapeArg)
soup = BeautifulSoup(fuel_price_html.text, features="html.parser")
fboTable=[]
for tr in soup.find_all('tr'):
    if tr.has_attr('id'):
        if str(tr['id']).find("fbo_") != -1:
            tab = tr.find_all('td')
            if len(tab) >= 7:
                distanceStr=tab[6].string
                dist=distanceStr[:distanceStr.find("NM")]
                fboTable.append({'airport':tab[1].string, 'fbo_name':tab[2].string, 'self':tab[3].string, 'full':tab[4].string, 'update':tab[5].string, 'dist':int(dist)})

if len(fboTable) == 0:
    sys.exit("No fuel sources found near " + airportCode + ".")

if len(airportCode) == 3:
    kCode = "K" + airportCode
    pCode = "P" + airportCode
else:
    kCode = pCode = airportCode

fboTable.sort(key=minDist)

print("-----------100LL PRICES AT " + airportCode + "-----------\n")
print("\tSELF\tFULL\t\t\tFBO")
for fbo in fboTable:
    if fbo['airport'] == kCode or fbo['airport'] == pCode or fbo['dist'] == 0:
        print("\t" + fbo['self'] + "\t" + fbo['full'] + "\t\t\t" + fbo['fbo_name'])

print("\n\n-----------100LL PRICES NEARBY-----------\n")
print("AIRPORT\tSELF\tFULL\tDISTANCE\tFBO")
for fbo in fboTable:
    if fbo['airport'] != kCode and fbo['airport'] != pCode and fbo['dist'] <= maxDist:
        print(fbo['airport'] + "\t" + fbo['self'] + "\t" + fbo['full'] + "\t" + str(fbo['dist']) + " nm \t\t" + fbo['fbo_name'])