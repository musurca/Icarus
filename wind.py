'''
    wind.py

    Determine wind speed and direction by taking distance and bearing
    to a fixed reference point over a time interval.

    1) Point your aircraft on a course directly toward
       or directly away from a fixed reference point 
       with distance measuring equipment (e.g., a VOR), 
       then set autopilot to maintain heading, altitude, 
       and speed.
    2) Record distance to reference point, start the 
       clock, and wait. Longer time intervals will 
       produce more accurate results. 300-600 seconds 
       (5-10 minutes) is ideal.
    4) After X seconds, record the new distance to 
       reference point as well as your plane's 
       deviation from its bearing.
    5) Enter numbers into program to determine 
       wind speed and direction.
       
'''

from math import sin, cos, sqrt, radians, degrees, asin

from utils import globenav

print("")
alt = float(input("Altitude (ft ASL): "))
ias = float(input("Indicated airspeed (kts): "))
d0 = float(input("TIME 0: Distance reading (nm): "))
d1 = float(input("TIME 1: Distance reading (nm): "))
dev = float(input("Course deviation (degrees, +/right, -/left): "))
t = float(input("Time between readings (seconds): "))

if d1 > d0:
   # if we're moving away, just flip the distances 
   d1, d0 = d0, d1

tas = ias + ias*0.02*alt/1000
t = t / (60*60)
deltaDist = d0 - t*tas

windMag = sqrt(d1**2 + deltaDist**2 - 2*d1*deltaDist*cos(radians(dev)))
direction = degrees(asin( d1 * sin(radians(dev)) / windMag ))
direction = globenav.wrap_brg(180 + globenav.wrap_brg(-direction))

windSpeed = windMag/t

moveDist = sqrt(d1**2 + d0**2 - 2*d1*d0*cos(radians(dev)))
groundspeed = moveDist/t

windDirFrom = int(round(direction))

print("")
print("TAS / GS  : " + str(int(round(tas))) + " kts / " + str(int(round(groundspeed))) + " kts\n")
print("  Wind    : " + str(windDirFrom)  + "° @ " + str(int(round(windSpeed))) + " kts")
print("")