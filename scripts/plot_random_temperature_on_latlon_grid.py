import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation
from noise import pnoise3  # Perlin noise in 3D

# Grid definition
lon = np.linspace(-180, 180, 360)
lat = np.linspace(-90, 90, 180)
lon2d, lat2d = np.meshgrid(lon, lat)

# Parameters
n_frames = 100
scale = 0.05  # spatial scale of noise
time_scale = 0.02  # temporal scale of noise
seed = 42

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
fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
mesh = ax.pcolormesh(lon, lat, np.zeros_like(lat2d), transform=ccrs.PlateCarree(), cmap='coolwarm')

# Update function for animation
def update(frame):
    temp = generate_temperature_field(frame)
    mesh.set_array(temp.ravel())
    ax.set_title(f"Frame {frame}")
    return [mesh]

# Animate
ani = FuncAnimation(fig, update, frames=n_frames, interval=100)
plt.show()

