"""
    magvar.py
    
    Simple interface to retrieve magnetic variation via IGRF-13 model.
    Based on code by Ciaran Beggan (British Geological Survey)
    https://github.com/zzyztyy/pyIGRF

"""

from datetime import date

from scipy import interpolate

import igrf.igrf_utils as iut

IGRF_FILE = r'./igrf/data/IGRF13.shc'

class Magvar:
    def __init__(self):
        self.igrf = iut.load_shcfile(IGRF_FILE, None)

    def declination(self, latd, lond, altft):
        igrf = self.igrf
        lat, lon = iut.check_lat_lon_bounds(latd,0,lond,0)
        colat = 90-lat
        itype = 1 # use geodetic model
        altkm = 0.0003048*altft
        year = date.today().year
        alt, colat, sd, cd = iut.gg_to_geo(altkm, colat)

        # Interpolate the geomagnetic coefficients to the desired date(s)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value='extrapolate')
        coeffs = f(year)    

        # Compute the main field B_r, B_theta and B_phi value for the location(s) 
        Br, Bt, Bp = iut.synth_values(coeffs.T, alt, colat, lon,
                                igrf.parameters['nmax'])

        # For the SV, find the 5 year period in which the date lies and compute
        # the SV within that period. IGRF has constant SV between each 5 year period
        # We don't need to subtract 1900 but it makes it clearer:
        epoch = (year-1900)//5    
        epoch_start = epoch*5
        # Add 1900 back on plus 1 year to account for SV in nT per year (nT/yr):
        coeffs_sv = f(1900+epoch_start+1) - f(1900+epoch_start)   
        Brs, Bts, Bps = iut.synth_values(coeffs_sv.T, alt, colat, lon,
                                igrf.parameters['nmax'])

        # Use the main field coefficients from the start of each five epoch
        # to compute the SV for Dec, Inc, Hor and Total Field (F) 
        # [Note: these are non-linear components of X, Y and Z so treat separately]
        coeffsm = f(1900+epoch_start);
        Brm, Btm, Bpm = iut.synth_values(coeffsm.T, alt, colat, lon,
                                igrf.parameters['nmax'])


        # Rearrange to X, Y, Z components 
        X = -Bt; Y = Bp; Z = -Br
        # For the SV
        dX = -Bts; dY = Bps; dZ = -Brs 
        Xm = -Btm; Ym = Bpm; Zm = -Brm
        # Rotate back to geodetic coords if needed
        if (itype == 1):
            t = X; X = X*cd + Z*sd;  Z = Z*cd - t*sd
            t = dX; dX = dX*cd + dZ*sd;  dZ = dZ*cd - t*sd
            t = Xm; Xm = Xm*cd + Zm*sd;  Zm = Zm*cd - t*sd
            
        # Compute the four non-linear components 
        dec, hoz, inc, eff = iut.xyz2dhif(X,Y,Z)
        # The IGRF SV coefficients are relative to the main field components 
        # at the start of each five year epoch e.g. 2010, 2015, 2020
        decs, hozs, incs, effs = iut.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)
        return decs