# Icarus
 CLI tools for General Aviation.

![Example](https://github.com/musurca/Icarus/raw/master/images/screen.png)

## Tools
### airportinfo
```
airportinfo [ICAO]

ex:
> airportinfo KLAX
```
Prints out useful information about an airport, including:
* latitude / longitude and altitude
* nearest city
* runway length, orientation, material, and suitability for night operations
* relevant radio frequencies
* nearby navaids
* nearby airports

NOTE: All headings are magnetic, calculated by magnetic declination at the airport on the current date via the IGRF-13 model.

### diagram
```
diagram [ICAO]

ex: 
> diagram KJFK
```
Downloads all available airport diagrams (PDF), approach/departure charts (PDF), and current remarks (TXT) to ./diagrams/[ICAO]. Remarks are also decoded/expanded where possible.

### distance
```
distance [ICAO origin] [ICAO destination]

ex:
> distance KSBA TRM 
```
Prints out distance and magnetic heading from one ICAO location to another. Either origin or destination may be either an airport or a navaid.

### fuel
```
fuel [ICAO] [100LL OR JETA]

ex:
> fuel KSAN JETA
```
Prints current fuel prices (either 100LL or Jet-A) at ICAO location, and within 100 nm.

### updatedb
```
updatedb
```
Downloads most recent database of airports, navaids, and radio frequencies.

## Dependencies
* [Python 3](https://www.python.org/downloads/)
* numpy
* scipy 
* wget 
* BeautifulSoup 4
* [rich](https://github.com/willmcgugan/rich)

1) [Download and install latest release of Python 3.](https://www.python.org/downloads/)

2) From the command line:
```
pip install numpy scipy wget beautifulsoup4 rich
```

## Acknowledgements
Airport/navaid data courtesy of [OurAirports](http://ourairports.com).
U.S. city data courtesy of [SimpleMaps](https://simplemaps.com/data/us-cities).
Some code based on the MIT-licensed [pyIGRF](https://github.com/zzyztyy/pyIGRF).