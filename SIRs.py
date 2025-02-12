# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 12 / 02 / 2025
# --------------------------------------------------------------------------------------------------------------------------------------
import subprocess
import sys
# --------------------------------------------------------------------------------------------------------------------------------------
# Function to install a package
# --------------------------------------------------------------------------------------------------------------------------------------

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------

install_package("sunpy")
install_package("astropy")

# --------------------------------------------------------------------------------------------------------------------------------------

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator

import astropy.units as u
from astropy.coordinates import Longitude

from sunpy.coordinates import HeliocentricEarthEcliptic, get_body_heliographic_stonyhurst, get_horizons_coord
from sunpy.time import parse_time

# --------------------------------------------------------------------------------------------------------------------------------------

obstime = parse_time('2008-JAN-23 16:39:33')

hee_frame = HeliocentricEarthEcliptic(obstime=obstime)

def get_first_orbit(coord):
    lon = coord.transform_to(hee_frame).spherical.lon
    shifted = Longitude(lon - lon[0])
    ends = np.flatnonzero(np.diff(shifted) < 0)
    if ends.size > 0:
        return coord[:ends[0]]
    return coord

planets = ['Earth']
times = obstime + np.arange(700) * u.day
planet_coords = {planet: get_first_orbit(get_body_heliographic_stonyhurst(planet, times))
                 for planet in planets}

stereo_a = get_horizons_coord('STEREO-A', obstime)
stereo_b = get_horizons_coord('STEREO-B', obstime)

print('---------------------------------------------------------------------')

def coord_to_heexy(coord):
    coord = coord.transform_to(hee_frame)
    coord.representation_type = 'cartesian'
    return coord.y.to_value('AU'), coord.x.to_value('AU')

mpl.rcParams.update({'figure.facecolor': 'white',
                     'axes.edgecolor': 'black',
                     'axes.facecolor': 'white',
                     'axes.labelcolor': 'black',
                     'axes.titlecolor': 'black',
                     'lines.linewidth': 2,
                     'xtick.color': 'black',
                     'xtick.direction': 'in',
                     'xtick.top': True,
                     'ytick.color': 'black',
                     'ytick.direction': 'in',
                     'ytick.right': True})

fig = plt.figure()
ax = fig.add_subplot()

ax.set_xlim(-2.15, 2.15)
ax.set_xlabel('Y (HEE)')
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_minor_locator(MultipleLocator(0.1))

ax.set_ylim(1.8, -1.8)
ax.set_ylabel('X (HEE)')
ax.yaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))

#ax.set_title(obstime.strftime('%d-%b-%Y %H:%M UT'))
ax.set_aspect('equal')

ax.plot([0, 0], [0, 2], linestyle='dotted', color='gray')

for planet, coord in planet_coords.items():
    ax.plot(*coord_to_heexy(coord), linestyle='dashed', color='gray')

    if planet == 'Earth':
        color, markersize, offset = 'lime', 10, 0.1
    else:
        color, markersize, offset = 'gray', None, 0.05

    x, y = coord_to_heexy(coord[0])
    ax.plot(x, y, 'o', markersize=markersize, color=color)
    ax.text(x + offset, y + offset, planet, color=color)

for stereo, label, color in [(stereo_a, 'A', 'red'), (stereo_b, 'B', 'blue')]:
    x, y = coord_to_heexy(stereo)
    #print(y,x)
    if label == 'A':
        sta_x, sta_y = y, x
    elif label == 'B':
        stb_x, stb_y = y, x
    #ax.plot([0, 5*x], [0, 5*y], linestyle='dotted', color='gray')
    ax.plot(x, y, 'o', color=color)
    ax.text(x + 0.1, y, label, color=color, fontsize=10)

ax.plot(0, 0, 'o', markersize=15, color='orange')
ax.text(0.12, 0, 'Sun', color='orange')

ax.plot([0,sta_y], [0,sta_x], linestyle='dotted', color='red')
ax.plot([0,stb_y], [0,stb_x], linestyle='dotted', color='blue')

# --------------------------------------------------------------------------------------------------------------------------------------
