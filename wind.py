'''
    wind.py

    Determine wind speed and direction by taking distance and bearing
    to a fixed reference point over a time interval.
       
'''
import npyscreen

from math import sin, cos, sqrt, radians, degrees, asin

from utils import globenav

result=""

class WindApp(npyscreen.NPSApp):
   def main(self):
      F = npyscreen.Form(name = "ICARUS - Wind Aloft Calculator",)
      altV  = F.add(npyscreen.TitleText, name = "Altitude (ft ASL):",)
      iasV = F.add(npyscreen.TitleText, name = "Indicated airspeed (kts):",)
      headV = F.add(npyscreen.TitleText, name = "Heading (degrees):",)
      d0V = F.add(npyscreen.TitleText, name = "1st distance reading (nm):",)
      d1V = F.add(npyscreen.TitleText, name = "2nd distance reading (nm):",)
      devV = F.add(npyscreen.TitleText, name = "Course deviation (degrees, +/right, -/left): ",)
      tV = F.add(npyscreen.TitleText, name = "Time between readings (seconds): ",)
      
      formIncomplete=True
      while formIncomplete:
         F.edit()

         try:
            alt = float(altV.get_value())
            ias = float(iasV.get_value())
            heading = float(headV.get_value())
            d0 = float(d0V.get_value())
            d1 = float(d1V.get_value())
            dev = float(devV.get_value())
            t = float(tV.get_value())
            formIncomplete=False
         except ValueError:
            formIncomplete=True

      if d1 > d0:
         # if we're moving away, just flip the distances 
         d1, d0 = d0, d1

      tas = ias + ias*0.02*alt/1000
      t = t / (60*60)
      deltaDist = d0 - t*tas

      windMag = sqrt(d1**2 + deltaDist**2 - 2*d1*deltaDist*cos(radians(dev)))
      direction = degrees(asin( d1 * sin(radians(dev)) / windMag ))
      direction = globenav.wrap_brg(180 + globenav.wrap_brg(-direction) + heading)

      windSpeed = windMag/t

      moveDist = sqrt(d1**2 + d0**2 - 2*d1*d0*cos(radians(dev)))
      groundspeed = moveDist/t

      windDirFrom = int(round(direction))

      result = "\nTAS / GS  : " + str(int(round(tas))) + " kts / " + str(int(round(groundspeed))) + " kts\n  Wind    : " + str(windDirFrom)  + "° @ " + str(int(round(windSpeed))) + " kts\n"
      npyscreen.notify_confirm(result, title="Result", form_color='STANDOUT', wrap=True, wide=False, editw=0)

if __name__ != "__main__":
   sys.exit()

App = WindApp()
App.run()