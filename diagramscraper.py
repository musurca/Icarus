'''
diagramscraper.py

Scrapes airnav.com for all relevant FAA diagrams for a particular airport.

'''
import requests
import sys
import os
import wget
import glob
from bs4 import BeautifulSoup

BASE_PATH = "./diagrams"

if len(sys.argv) > 1:
    airportCode = sys.argv[1].upper()
else:
    sys.exit("You must provide an airport ICAO code!")

# Create the diagram directory if needed
try:
    os.mkdir(BASE_PATH)
except OSError as error:
    pass

# Find all FAA PDF links
s = requests.Session() 
chart_soup = BeautifulSoup(s.get('https://www.airnav.com/airport/' + airportCode).text, features="html.parser")
pdfLinks = []
for a in chart_soup.find_all('a'):
    if a.has_attr('href'):
        hrefStr = str(a['href'])
        if hrefStr.find("aeronav.faa.gov") != -1:
            if hrefStr.find("?") != -1:
                 pdfLinks.append(hrefStr[hrefStr.find("?")+1:])
            else:
                pdfLinks.append(hrefStr)

if len(pdfLinks) == 0:
    sys.exit("Can't find an airport with the code " + airportCode + "!")

# Create the path for the airport, or remove old version
# if it already exists
try:
    os.mkdir(BASE_PATH + "/" + airportCode)
except OSError as error:
    for file in glob.glob(BASE_PATH + "/" + airportCode + "/*"):
        os.remove(file)

# Download them      
pdfLinks = list(dict.fromkeys(pdfLinks)) # remove duplicate urls
for url in pdfLinks:
    wget.download(url, BASE_PATH + "/" + airportCode)

print("\nDone!")