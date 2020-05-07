# Icarus
A suite of CLI tools for use in General Aviation and flight simulation.

![Example](https://github.com/musurca/Icarus/raw/master/images/screen.png)

## Tools
### airportinfo
```
airportinfo [ICAO]

ex:
> airportinfo KLAX
```
Displays useful information about an airport, including:
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
Connects to the FAA database and downloads all available airport diagrams (PDF), approach/departure charts (PDF), and current remarks (TXT) to ./diagrams/[ICAO]. Remarks are also decoded/expanded where possible.

### distance
```
distance [ICAO origin] [ICAO destination]

ex:
> distance KSBA TRM 
```
Displays the distance and magnetic heading on a direct course from one ICAO location to another. Either origin or destination may be either an airport or a navaid.

### fuel
```
fuel [ICAO] [100LL OR JETA] [range]

ex:
> fuel KSAN JETA
```
Displays current avgas prices (either 100LL or Jet-A) at ICAO location, and within a desired range (100 nm by default).

### rangeroute
```
rangeroute [ICAO origin] [ICAO destination] [max range in nm]

ex:
> rangeroute KBGR BGMQ 500
```
Finds the shortest route between two airports using multiple stops, in which the length of each leg of the trip is less than the maximum range of your aircraft specified.

NOTE: Due to the large number of possible airports to search, this command can be very slow to execute.

### updatedb
```
updatedb
```
Downloads most recent database of airports, navaids, and radio frequencies.

### vorroute
```
vorroute [ICAO origin] [ICAO destination]

ex:
> vorroute LFPG OMDB
```
Finds the shortest VOR-to-VOR route between two airports or navaids. You can filter by civilian, legacy, and military types.

### wind
```
wind
```
Estimates wind aloft by taking the results of two distance readings from a fixed reference point. The resulting information can be fed into an E6B to determine course correction for leeway.

How to use:
1) Point your aircraft on a course directly toward or directly away from a fixed reference point with distance measuring equipment (e.g., a VOR), then set autopilot to maintain heading, altitude, and speed.
2) Record distance to reference point, start a timer, and wait for X seconds. Longer time intervals will produce more accurate results. 300-600 seconds (5-10 minutes) is ideal.
3) After X seconds, record the new distance to the reference point as well as your plane's deviation from its original bearing.
4) Enter your recorded data into the wind program to calculate wind speed and direction.

## Dependencies
* [Python 3](https://www.python.org/downloads/)
* numpy
* scipy 
* wget 
* BeautifulSoup 4
* npyscreen 
* [rich](https://github.com/willmcgugan/rich)

1) [Download and install latest release of Python 3.](https://www.python.org/downloads/)

2) From the command line:
```
pip install numpy scipy wget beautifulsoup4 npyscreen rich
```

## Acknowledgements
Airport/navaid data courtesy of [OurAirports](http://ourairports.com).
U.S. city data courtesy of [SimpleMaps](https://simplemaps.com/data/us-cities).
Some code based on the MIT-licensed [pyIGRF](https://github.com/zzyztyy/pyIGRF).