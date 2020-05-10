'''
utils.py

Shared aviation utility methods.

'''
import csv
from math import sin, cos, sqrt, atan2, radians, degrees

DATA_DIR = "./data/"

# REMARK DECODING / EXPANSION

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
                "stas":"straight in approaches",
                "atct":"air traffic control tower",
                "lcl":"local",
                "trng":"training",
                "twy":"taxiway",
                "twys":"taxiways",
                "freq":"frequency",
                "freqs":"frequencies",
                "una":"unable",
                "agri":"agricultural",
                "excp":"except",
                "pwrd":"powered",
                "svcs":"services",
                "svc":"service",
                "mil":"military",
                "maint":"maintenance",
                "btn":"between",
                "lgtd":"lighted",
                "vcnty":"vicinity",
                "nmrs":"numerous",
                "turb":"turbulence",
                "rstd":"restricted",
                "flt":"flight",
                "ops":"operations",
                "gtr":"greater",
                "opn":"operation",
                "lgts":"lights",
                "authd":"authorized",
                "pwr":"power",
                "prkg":"parking",
                "trmls":"terminals",
                "intrpd":"interrupted",
                "mnm":"minimum",
                "psn":"position",
                "txg":"taxiing",
                "haz":"hazard",
                "inbd":"inbound",
                "obnd":"outbound",
                "sbnd":"southbound",
                "wbnd":"westbound",
                "nbnd":"northbound",
                "ebnd":"eastbound",
                "len":"length",
                "offl":"official",
                "bus":"business",
                "btwn":"between",
                "thld":"thrust hold",
                "sgl":"single",
                "eng":"engine",
                "grvl":"gravel",
                "lndg":"landing",
                "cntrln":"centerline",
                "hdg":"heading",
                "indef":"indefinitely",
                "indefly":"indefinitely",
                "mag":"magnetic",
                "pmtd":"permitted",
                "rwys":"runways",
                "rys":"runways",
                "arcft":"aircraft",
                "afct":"aircraft",
                "degs":"degrees",
                "obsc":"obscured",
                "blo":"below",
                "rstr":"restricted",
                "drg":"during",
                "nml":"normal",
                "opr":"operation",
                "psgrs":"passengers",
                "dsnt":"designated",
                "exc":"except",
                "lndgs":"landings",
                "tkofs":"takeoffs",
                "tkof":"takeoff",
                "annc":"announce",
                "act":"active",
                "publd":"published",
                "intxn":"intersection",
                "prvd":"provide",
                "ots":"out of service",
                "rlls":"lead-in light system",
                "ident":"identification",
                "aproxly":"approximately",
                "dstc":"distance",
                "addnl":"additional",
                "ppr":"prior permission required",
                "gen":"general",
                "avn":"aviation",
                "procd":"proceed",
                "mkd":"marked",
                "auzd":"authorized",
                "indus":"industrial",
                "instln":"installation",
                "trnspn":"transportation",
                "unlgt":"unlighted",
                "lgt":"lighted",
                "obstn":"obstruction",
                "afld":"airfield",
                "ldg":"landing",
                "dpt":"departing",
                "vsb":"visible",
                "fpl":"flight plan",
                "prk":"parking",
                "unauthd":"unauthorized",
                "mrk":"marking",
                "unavbl":"unavailable",
                "rqr":"requires",
                "gnd":"ground",
                "grd":"ground",
                "unlgtd":"unlighted",
                "daylt":"daylight"
            }

punctDict = ['/', '.', ';', ',', ' ', ':','(',')']

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


# RUNWAY MATERIAL DECODING

def runwayMaterial(txt):
    # no common vocab for this so we have to be a bit flexible
    surf = txt.upper()
    if surf.find("CON") != -1:
        return "Concrete"
    elif surf.find("ASP") != -1:
        return "Asphalt"
    elif surf.find("TUR") != -1:
        return "Astroturf"
    elif surf.find("DIRT") != -1:
        return "Dirt"
    elif surf.find("GRV") != -1 or surf.find("GRAV") != -1:
        return "Gravel"
    elif surf.find("SAND") != -1:
        return "Sand"
    elif surf.find("WAT") != -1:
        return "Water"
    elif surf.find("MAT") != -1:
        return "Mat"
    elif surf.find("GRASS") != -1:
        return "Grass"
    else:
        return ""

# SPHERICAL NAVIGATION

class globenav:
    # wrap a bearing in degrees to the range 0-359
    def wrap_brg(b):
        while deg < 0:
            deg = 360+deg
        while deg >= 360:
            deg = deg-360
        return deg

    # true bearing from one global point to another
    def brg_coord(lat1,lon1,lat2,lon2):
        # source: https://www.movable-type.co.uk/scripts/latlong.html
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)
        deltaLon = lon2 - lon1
        y = sin(deltaLon) * cos(lat2)
        x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(deltaLon)
        return globenav.wrap_brg(degrees(atan2(y, x)))

    # distance between two global points in nautical miles
    def dist_coord(lat1,lon1,lat2,lon2): 
        # source: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude  
        R = 6373.0 # approximate radius of earth in km
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return 0.539957*R * c

# CSV DATABASE QUERIES
class db:
    # execute a function on each element of a CSV
    def execute(csvFile, executeFunc):
        with open(DATA_DIR+csvFile, newline='') as csvfile:
            elements = csv.DictReader(csvfile)
            for element in elements:
                executeFunc(element)

    # return results filtered by a query function, and optionally post-process results
    def query(csvFile, queryFunc, processFunc=None):
        results = []
        with open(DATA_DIR+csvFile, newline='') as csvfile:
            elements = csv.DictReader(csvfile)
            for element in elements:
                res = queryFunc(element)
                if res[0]:
                    if processFunc != None:
                        processFunc(element, res[1:])
                    results.append(element)
        return results

    # return first element matching query function
    def findFirst(csvFile, queryFunc):
        with open(DATA_DIR+csvFile, newline='') as csvfile:
            elements = csv.DictReader(csvfile)
            for element in elements:
                if queryFunc(element):
                    return element
        return None

# SUBSTRING MATCHING

def longestSubstringFinder(string1, string2):
    #source: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): 
                    answer = match
                match = ""
    return answer
