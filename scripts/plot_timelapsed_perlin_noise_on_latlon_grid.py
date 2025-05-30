"""Plot perlin noise on Plate-Carree projection."""

from argparse import ArgumentParser, BooleanOptionalAction
import cartopy.crs as ccrs
from noise import pnoise3  # Perlin noise in 3D
import numpy as np
from numpy import ndarray
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os


def main():
    args = cli()

    # Get cli args
    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels

    outdir: str = args.outdir
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    save_each_frame: bool = args.save_each_frame
    num_frames_in_animation: int = args.num_frames_in_animation

    # Globe grid definition
    lon = np.linspace(-180, 180, 360)
    lat = np.linspace(-90, 90, 180)
    lon2d, lat2d = np.meshgrid(lon, lat)

    # Plot of noise on globe grid
    px = 1/plt.rcParams["figure.dpi"]
    fig = plt.figure(
        figsize=(plot_width_in_pixels * px, plot_height_in_pixels * px))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    noise = generate_perlin_noise_field_on_latlon_mesh(lat2d, lon2d)
    mesh = ax.pcolormesh(
        lon,
        lat,
        noise,
        transform=ccrs.PlateCarree(),
        cmap='coolwarm')

    animation = FuncAnimation(
        fig,
        update_frame(lat2d, lon2d, mesh, outdir, fig, save_each_frame),
        frames=num_frames_in_animation)

    animation.save(os.path.join(outdir, "anim.gif"))

    return


def cli():
    parser = ArgumentParser(
        description="Plot (and optionally save each frame) animation of Perlin"
                    " noise on Plate-Carree projection.")

    parser.add_argument("outdir", type=str,
                        help="destination directory of saved plots")

    parser.add_argument(
        "--save-each-frame",
        action=BooleanOptionalAction,
        help="True to save each frame of timelapsed noise on grid to `outdir`."
             " (default: False)",
        required=True,
        default=False)

    default_plot_width_in_pixels = 4096
    parser.add_argument(
        "--plot_width_in_pixels",
        type=int,
        help=f" (default: {default_plot_width_in_pixels})",
        default=default_plot_width_in_pixels)

    default_plot_height_in_pixels = 2048
    parser.add_argument(
        "--plot_height_in_pixels",
        type=int,
        help=f" (default: {default_plot_height_in_pixels})",
        default=default_plot_height_in_pixels)

    default_num_frames_in_animation = 366
    parser.add_argument(
        "--num-frames-in-animation",
        help=f"default: {default_num_frames_in_animation}",
        dest="num_frames_in_animation",
        type=int,
        default=default_num_frames_in_animation)

    args = parser.parse_args()

    return args


def update_frame(
        lat2d, lon2d, mesh, outdir, fig, save_each_frame: bool = False):
    def update(frame):
        noise = generate_perlin_noise_field_on_latlon_mesh(lat2d, lon2d, frame)
        mesh.set_array(noise.ravel())
        filename = os.path.join(outdir, f"frame_{frame}.png")
        # https://github.com/matplotlib/matplotlib/issues/2305#issuecomment-223996919
        if save_each_frame:
            fig.savefig(filename)
        return [mesh]
    return update


def generate_perlin_noise_field_on_latlon_mesh(
        lat2d: ndarray,
        lon2d: ndarray,
        timestep: int = 0,
        spatial_scale: float = 0.05,
        temporal_scale: float = 0.02,
        seed: int = 42):

    noise_field = np.zeros_like(lat2d)
    for i in range(lat2d.shape[0]):
        for j in range(lat2d.shape[1]):
            noise_field[i, j] = pnoise3(
                spatial_scale * lon2d[i, j],
                spatial_scale * lat2d[i, j],
                timestep * temporal_scale,
                repeatx=360,
                repeaty=180,
                base=seed)

    return noise_field


if __name__ == "__main__":
    main()
