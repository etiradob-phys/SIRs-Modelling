# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 17 / 02 / 2025
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
install_package("matplotlib")

# --------------------------------------------------------------------------------------------------------------------------------------

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator
from matplotlib.animation import FuncAnimation

import astropy.units as u
from astropy.coordinates import Longitude

from sunpy.coordinates import HeliocentricEarthEcliptic, get_body_heliographic_stonyhurst, get_horizons_coord
from sunpy.time import parse_time

# --------------------------------------------------------------------------------------------------------------------------------------

year = input("Enter the year: ")
month = input("Enter the month (e.g., JAN): ")
day = input("Enter the day: ")
hour = input("Enter the hour (24-hour format): ")
minute = input("Enter the minute: ")
second = input("Enter the second: ")

time_str = f"{year}-{month}-{day} {hour}:{minute}:{second}"

obstime = parse_time(time_str)

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

# Create a polar overlay sharing the same origin as the Cartesian plot:
ax_polar = fig.add_subplot(111, polar=True, label='polar', frame_on=False)

# Set the radial limit to match the Cartesian plot's limits:
ax_polar.set_ylim(0, 2.15)  # Match with the Cartesian x and y limits

# Align zero angle with the positive X-axis (HEE system):
ax_polar.set_theta_zero_location('S')                           
ax_polar.set_theta_direction(-1) 

# Customize polar grid for better visibility:
ax_polar.grid(color='gray', linestyle='dotted', alpha=0.7)

# Hide radial labels to avoid clutter:
ax_polar.set_yticklabels([])

# Make the polar grid transparent to overlay nicely:
ax_polar.patch.set_alpha(0.0)

# Get the current theta tick labels:
angle_labels = ax_polar.get_xticklabels()

# Hide the 0º label (first label in the list):
angle_labels[0].set_visible(False)

ax_polar.set_rgrids([])  # Hides the radial grid lines (circles)

plt.show()
