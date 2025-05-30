"""Plot perlin noise on arbitrary pixel Plate-Care projection."""

from argparse import ArgumentParser, BooleanOptionalAction
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation
from noise import pnoise3  # Perlin noise in 3D
import sys 

# define CLI 
parser = ArgumentParser(
    description="Plot (and save) animation of perlin noise on Plate-Care projection.")

default_width = 4096
parser.add_argument(
    "width", 
    type=int, 
    help="width of image in pixels (default: {default_width})", 
    default=default_width)

default_height = 2048
parser.add_argument(
    "height", 
    type=int, 
    help=f"height of image in pixels (default: {default_height}", 
    default=default_height)

default_num_frames_in_animation = 366
parser.add_argument(
    "--num-frames-in-animation", 
    help=f"default: {default_num_frames_in_animation}"
    dest="num_frames_in_animation", 
    type=int,
    default=num_frames_in_animation)

parser.add_argument("--animate", action=BooleanOptionalAction)

default_dpi = 100
parser.add_argument("--dpi", type=int, default=f"default: {default_dpi}")

args = parser.parse_args()

# Get cli args
width : int = args.width 
height : int = args.height  
num_frames_in_animation : int = args.num_frames_in_animation 
animate : bool = args.animate 
dpi : int = args.dpi 

# Grid definition
lon = np.linspace(-180, 180, 360)
lat = np.linspace(-90, 90, 180)
lon2d, lat2d = np.meshgrid(lon, lat)

# Parameters for perlin noise 
spatial_scale_of_perlin_noise = 0.05  
temporal_scale_of_perlin_noise = 0.02  
perlin_noise_seed = 42     

# Function to generate fluid-like Perlin noise
def generate_temperature_field(t, scale=0.05, time_scale=0.02):
    noise_field = np.zeros_like(lat2d)
    for i in range(lat2d.shape[0]):
        for j in range(lat2d.shape[1]):
            noise_field[i, j] = pnoise3(
                spatial_scale_of_perlin_noise * lon2d[i, j],
                spatial_scale_of_perlin_noise * lat2d[i, j],
                t * temporal_scale_of_perlin_noise,
                repeatx=360, repeaty=180, base=perlin_noise_seed
            )
    return noise_field

# Set up plot
# https://stackoverflow.com/questions/13714454/specifying-and-saving-a-figure-with-exact-size-in-pixels
fig = plt.figure(figsize=(x/dpi, y/dpi))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
temp = generate_temperature_field(0)
mesh = ax.pcolormesh(
    lon, 
    lat, 
    temp,
    transform=ccrs.PlateCarree(), 
    cmap='coolwarm')

# Update function for animation
def update(frame):
    temp = generate_temperature_field(frame)
    mesh.set_array(temp)
    filename=f"data/frame_{frame:03}.png"
    # https://github.com/matplotlib/matplotlib/issues/2305#issuecomment-223996919
    plt.savefig(filename, dpi=dpi)
    return [mesh]

# Animate
if animate:
    ani = FuncAnimation(fig, update, frames=num_frames_in_animation, interval=100)
plt.show()

