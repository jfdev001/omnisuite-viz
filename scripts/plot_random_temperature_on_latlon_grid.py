"""Plot perlin noise on arbitrary pixel Plate-Care projection. 

usage: $0 x y animate

where animate is {0,1}
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation
from noise import pnoise3  # Perlin noise in 3D
import sys 


if len(sys.argv) == 1:
    x = 512
    y = 512
    animate = 1 
else:
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    animate = int(sys.argv[3])

# Grid definition
lon = np.linspace(-180, 180, 360)
lat = np.linspace(-90, 90, 180)
lon2d, lat2d = np.meshgrid(lon, lat)

# Parameters
n_frames = 366
scale = 0.05  # spatial scale of noise
time_scale = 0.02  # temporal scale of noise
seed = 42
dpi = 100

# Function to generate fluid-like Perlin noise
def generate_temperature_field(t, scale=0.05, time_scale=0.02):
    noise_field = np.zeros_like(lat2d)
    for i in range(lat2d.shape[0]):
        for j in range(lat2d.shape[1]):
            noise_field[i, j] = pnoise3(
                scale * lon2d[i, j],
                scale * lat2d[i, j],
                t * time_scale,
                repeatx=360, repeaty=180, base=seed
            )
    return noise_field

# Set up plot
# https://stackoverflow.com/questions/13714454/specifying-and-saving-a-figure-with-exact-size-in-pixels
fig = plt.figure(figsize=(x/dpi, y/dpi), dpi=dpi)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
temp = generate_temperature_field(0)
mesh = ax.pcolormesh(
    lon, lat, 
    temp,
    transform=ccrs.PlateCarree(), 
    cmap='coolwarm')

# Update function for animation
def update(frame):
    temp = generate_temperature_field(frame)
    mesh.set_array(temp)
    filename=f"data/frame_{frame:03}.png"
    # https://github.com/matplotlib/matplotlib/issues/2305#issuecomment-223996919
    plt.savefig(filename, dpi='figure')
    return [mesh]

# Animate
if animate:
    ani = FuncAnimation(fig, update, frames=n_frames, interval=100)
plt.show()

