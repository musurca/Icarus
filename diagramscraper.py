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

if len(pdfLinks) == 0:
    print("No diagrams available for this airport.")
else:
    # remove old diagrams & remarks
    for file in glob.glob(BASE_PATH + "/" + airportCode + "/*"):
        os.remove(file)

    # Download them      
    for link in pdfLinks:
        print("\n" + link['text'])
        wget.download(link['url'], BASE_PATH + "/" + airportCode + "/" + link['text'] + ".PDF")

# save decoded airport remarks
remarkDict = {  'opns':"operations",
                'dsgnd':"designated",
                'heli':"helipad",
                'extdd':"extended",
                'dep':"departure",
                'deps':"departures",
                'apch':"approach",
                'apchs':"approaches",
                'rsrtd':"restricted",
                'auth':"authorized",
                'mntn':"maintain",
                'ry':"runway",
                "rwy":"runway",
                'ne':"northeast",
                'sw':"southwest",
                "se":"southeast",
                "nw":"northwest",
                "n":"north",
                "s":"south",
                "e":"east",
                "w":"west",
                "prmary":"primary",
                "ohd":"overhead",
                "fm":"from",
                "byd":"beyond",
                "rcmdd":"recommended",
                "pat":"pattern", 
                "deg":"degree",
                "oper":"operating",
                "arpt":"airport",
                "hel":"helicopters",
                "mt":"mountain",
                "ovr":"over",
                "ctc":"contact",
                "lctd":"located",
                "artcc":"air route traffic control center",
                "atcc":"air traffic control center",
                "tsnt":"transient",
                "clsd":"closed",
                "pvt":"private",
                "sfc":"surface",
                "acft":"aircraft",
                "psnl":"personnel",
                "efct":"effect",
                "lmtd":"limited",
                "trml":"terminal",
                "non-sked":"non-scheduled",
                "sked":"scheduled",
                "trnsp":"transport",
                "rqrd":"required",
                "arr":"arrival",
                "intl":"international",
                "emerg":"emergency",
                "fac":"facility",
                "facs":"facilities",
                "avbl":"available",
                "proc":"procedure",
                "procs":"procedures",
                "hrs":"hours",
                "coml":"commercial",
                "tfc":"traffic",
                "invof":"in the vicinity of",
                "mi":"mile",
                "sta":"straight in approach",
                "stas":"straight in approaches"
            }

punctDict = ['/', '.', ';', ',', ' ']

def customSplit(str):
    tokens=[]
    cur=0
    for k in range(len(str)):
        if str[k] in punctDict:
            if k == cur:
                word = ""
            else:
                word = str[cur:k]
            tokens.append({'word':word,'punct':str[k]})
            cur=k+1
    if cur < len(str):
        tokens.append({'word':str[cur:],'punct':""})
    return tokens

def decode_remark(rtext):
    finalTxt = ""
    tokens = customSplit(rtext.lower())
    for token in tokens:
        if token['word'] in remarkDict.keys():
            word = remarkDict[token['word']]
        else:
            word = token['word']
        finalTxt = finalTxt + word + token['punct']
    return finalTxt

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