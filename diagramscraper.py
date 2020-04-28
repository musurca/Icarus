'''
diagramscraper.py

Scrapes the FAA website for all relevant diagrams for a particular airport.

'''
import requests
import sys
import os
import wget
import glob
from bs4 import BeautifulSoup

from utils import decode_remark

BASE_PATH = "./diagrams"

CHART_SOURCE = 'https://nfdc.faa.gov/nfdcApps/services/ajv5/airportDisplay.jsp?airportId='

if len(sys.argv) > 1:
    airportCode = sys.argv[1].upper()
else:
    sys.exit("You must provide an airport ICAO code!")

# Create the diagram & airport directory if needed
try:
    os.mkdir(BASE_PATH)
except OSError as error:
    pass
try:
   os.mkdir(BASE_PATH + "/" + airportCode)
except OSError as error:
    pass

# Find all FAA PDF links
s = requests.Session() 
chart_soup = BeautifulSoup(s.get(CHART_SOURCE + airportCode).text, features="html.parser")
pdfLinks = []
for a in chart_soup.find_all('a'):
    if a.has_attr('href'):
        hrefStr = str(a['href'])
        if hrefStr.find("aeronav.faa.gov") != -1 and hrefStr.find("PDF") != -1:
            if hrefStr.find("?") != -1:
                 pdfLinks.append({'text':a.text, 'url':hrefStr[hrefStr.find("?")+1:]})
            else:
                pdfLinks.append({'text':a.text, 'url':hrefStr})

def replace_char(s, p, r):
    return s[:p]+r+s[p+1:]

if len(pdfLinks) == 0:
    print("No diagrams available for this airport.")
else:
    # remove old diagrams & remarks
    for file in glob.glob(BASE_PATH + "/" + airportCode + "/*"):
        os.remove(file)

    # Download them      
    for link in pdfLinks:
        # replace folder separator character
        fileName = link['text']
        splatIndex = fileName.find("/")
        while splatIndex != -1:
            fileName = replace_char(fileName,splatIndex,'-')
            splatIndex = fileName.find("/")
        print("\n" + fileName)
        wget.download(link['url'], BASE_PATH + "/" + airportCode + "/" + fileName + ".PDF")

# save decoded airport remarks
remarks = []
for div in chart_soup.find_all('div'):
    if div.has_attr('id'):
        if div['id'].find("remarks") != -1:
            for remark in div.find_all('li'):
                remarks.append(decode_remark(remark.text).upper())

if len(remarks) > 0:
    outF = open(BASE_PATH + "/" + airportCode + "/" + "REMARKS.TXT", "w")
    outF.write("                    " + airportCode + " REMARKS\n")
    outF.write("------------------------------------------------------\n")
    for remark in remarks:
        outF.write("* " + remark + "\n")
    outF.close()
    print("\nREMARKS")

print("\nDone! Saved to " + BASE_PATH + "/" + airportCode + ".")