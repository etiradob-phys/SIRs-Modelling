# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 22 / 02 / 2025
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
install_package("scipy")

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

## Create a polar overlay sharing the same origin as the Cartesian plot:
#ax_polar = fig.add_subplot(111, polar=True, label='polar', frame_on=False)

## Set the radial limit to match the Cartesian plot's limits:
#ax_polar.set_ylim(0, 2.15)  # Match with the Cartesian x and y limits

## Align zero angle with the positive X-axis (HEE system):
#ax_polar.set_theta_zero_location('S')                           
#ax_polar.set_theta_direction(-1) 

## Customize polar grid for better visibility:
#ax_polar.grid(color='gray', linestyle='dotted', alpha=0.7)

## Hide radial labels to avoid clutter:
#ax_polar.set_yticklabels([])

## Make the polar grid transparent to overlay nicely:
#ax_polar.patch.set_alpha(0.0)

## Get the current theta tick labels:
#angle_labels = ax_polar.get_xticklabels()

## Hide the 0° label (first label in the list):
#angle_labels[0].set_visible(False)

#ax_polar.set_rgrids([])  # Hides the radial grid lines (circles)

#plt.show()

# --------------------------------------------------------------------------------------------------------------------------------------

# Parameters:

T_sun = 25.38 * 24 * 3600
omega_sun = 2 * np.pi / T_sun

r_min = 0.3
r_max = 2.5
n_points = 50

v_sw_slow = 294
v_sw_fast = (v_sw_slow + 400)

v_sw_slow_AU = v_sw_slow / 1.496e8
v_sw_fast_AU = v_sw_fast / 1.496e8

r0 = (np.linspace(r_min, r_max, n_points))

phi_slow = (omega_sun * (r0 - r_min) / v_sw_fast_AU)
phi_fast = (omega_sun * (r0 - r_min) / v_sw_slow_AU)

# Initial positions of points on the spiral:

x_array_slow_t0 = (r0 * np.cos(phi_slow))
y_array_slow_t0 = (r0 * np.sin(phi_slow))

x_array_fast_t0 = (r0 * np.cos(phi_fast))
y_array_fast_t0 = (r0 * np.sin(phi_fast))

# Rotate the spiral by an angle in degrees:

angle2Earth = (46) * (-1)
angle = (angle2Earth + 90)

theta_angle = (angle) * (np.pi / 180)

x_array_slow_t0_new = (y_array_slow_t0 * np.cos(theta_angle) - x_array_slow_t0 * np.sin(theta_angle))
y_array_slow_t0_new = (y_array_slow_t0 * np.sin(theta_angle) + x_array_slow_t0 * np.cos(theta_angle))

x_array_fast_t0_new = (y_array_fast_t0 * np.cos(theta_angle) - x_array_fast_t0 * np.sin(theta_angle))
y_array_fast_t0_new = (y_array_fast_t0 * np.sin(theta_angle) + x_array_fast_t0 * np.cos(theta_angle))

# Define rotation angles (in radians):

theta_values = np.arange(0, 360, 1) * (np.pi / 180)

spiral_line_slow, = ax.plot([], [], color='deepskyblue')
scatter_points_slow = ax.scatter([], [], s=7, zorder=1, color='skyblue', marker=".")

spiral_line_fast, = ax.plot([], [], color='deepskyblue')
scatter_points_fast = ax.scatter([], [], s=7, zorder=1, color='deepskyblue', marker=".")

# Create a text element for the timestamp:
time_text = ax.text(0.5, -2.0, '', color='black', fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

previous_frame = -1

# Initialize (overwrite) the file at the start
with open('spiral_data.txt', 'w') as file:
    file.write("Spiral Data Log\n\n")

# Update function for animation
def update(frame):
    global previous_frame

    # If the frame is the same as the previous one, don't print:
    if frame == previous_frame:
        return spiral_line_slow, scatter_points_slow, spiral_line_fast, scatter_points_fast, time_text

    # Update previous frame to the current one:
    previous_frame = frame

    theta = theta_values[frame]

    # Growing factor (gradually increases from 0 to 1)

    scale_ani = 1#frame / len(theta_values)

    # Rotate the spiral:

    x_rot_slow = (scale_ani * (x_array_slow_t0_new * np.cos(theta) - y_array_slow_t0_new * np.sin(theta)))
    y_rot_slow = (scale_ani * (x_array_slow_t0_new * np.sin(theta) + y_array_slow_t0_new * np.cos(theta)))

    x_rot_fast = (scale_ani * (x_array_fast_t0_new * np.cos(theta) - y_array_fast_t0_new * np.sin(theta)))
    y_rot_fast = (scale_ani * (x_array_fast_t0_new * np.sin(theta) + y_array_fast_t0_new * np.cos(theta)))

    x_rot_slow = (x_rot_slow) * (-1)
    y_rot_slow = (y_rot_slow) * (-1)

    x_rot_fast = (x_rot_fast) * (-1)
    y_rot_fast = (y_rot_fast) * (-1)

    distances_slow = np.sqrt((x_rot_slow - 1)**2 + (y_rot_slow)**2)
    distances_fast = np.sqrt((x_rot_fast - 1)**2 + (y_rot_fast)**2)

    # Update the scatter points:
    scatter_points_slow.set_offsets(np.column_stack((y_rot_slow, x_rot_slow)))
    scatter_points_fast.set_offsets(np.column_stack((y_rot_fast, x_rot_fast)))

    # Update spiral line (plot slow spiral first, then fast)
    spiral_line_slow.set_data(y_rot_slow, x_rot_slow)
    spiral_line_fast.set_data(y_rot_fast, x_rot_fast) 

    # Compute and update time
    time_offset = 1.927
    current_time = obstime + frame * time_offset * u.hour
    time_text.set_text(current_time.strftime('%d-%b-%Y %H:%M UT'))
    current_date_str = current_time.strftime('%d-%b-%Y %H:%M UT')

    # Print the (x, y) coordinates and distances for each point as it rotates:
#    print(f"Frame {frame} - Date: {current_date_str}:")
#    for x_s, y_s, d_s in zip(y_rot_slow, x_rot_slow, distances_slow):
#        print(f"Slow Spiral - x: {x_s:.3f}, y: {y_s:.3f}, Distance to Earth [AU]: {d_s:.3f}")
#    for x_f, y_f, d_f in zip(y_rot_fast, x_rot_fast, distances_fast):
#        print(f"Fast Spiral - x: {x_f:.3f}, y: {y_f:.3f}, Distance to Earth [AU]: {d_f:.3f}")

    # Save (x_f, y_f, d_f) to a text file (overwritten at the start of the animation):
    with open('spiral_data.txt', 'a') as file:
        file.write(f"Frame {frame} - Date: {current_date_str}:\n")
        for x_f, y_f, d_f in zip(y_rot_fast, x_rot_fast, distances_fast):
            file.write(f"Fast Spiral - x: {x_f:.3f}, y: {y_f:.3f}, Distance to Earth [AU]: {d_f:.3f}\n")
        file.write("\n")  # Add a newline for better readability

    return spiral_line_slow, scatter_points_slow, spiral_line_fast, scatter_points_fast, time_text

# Create animation
ani = FuncAnimation(fig, update, frames=len(theta_values), interval=100, blit=True)

plt.show()
