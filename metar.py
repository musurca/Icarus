'''
metar.py

Retrieves the current METAR for an airport or weather station.

'''

import sys
from rich.console import Console
from rich.markdown import Markdown

from bs4 import BeautifulSoup

from utils import scrape

METAR_SOURCE        = 'https://aviationweather.gov/metar/data?format=raw&date=&hours=0&ids='

console = Console()
s = scrape.getSession()

if len(sys.argv) > 1:
    code = sys.argv[1].upper()
else:
    sys.exit("You must provide an ICAO code!")

metarTxt = ""
soup = scrape.getSoup(s, METAR_SOURCE + code)
metarSoup = soup.find_all('code')
if len(metarSoup) > 0:
    checkMetar = metarSoup[0].get_text().split()
    if checkMetar[0] == code:
        for i in range(len(checkMetar)):
            if i != 0:
                metarTxt = metarTxt + checkMetar[i] + " "
if metarTxt == "":
    sys.exit("Can't find a METAR for that code!")

console.print(metarTxt)
print("")