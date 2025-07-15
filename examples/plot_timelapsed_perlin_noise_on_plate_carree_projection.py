from argparse import ArgumentParser, BooleanOptionalAction
from numpy import zeros_like
from noise import pnoise3
import os

from omnisuite_viz.animator import OmniSuiteWorldMapAnimator
from omnisuite_viz.animator_config import OmniSuiteAnimatorConfig
from omnisuite_viz.grid import WorldMapRectangularGrid

DESCRIPTION = """
Save animation frames (and optionally combine the frames to a gif) of Perlin
noise on Plate-Carree projection. A trivial example with artificial data.
"""


def main():
    # save and annotate cli args
    args = cli()

    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels

    output_dir: str = args.output_dir
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    save_animation: bool = args.save_animation
    num_frames_in_animation: int = args.num_frames_in_animation

    # perform animation
    grid = WorldMapRectangularGrid()

    config = OmniSuiteAnimatorConfig(  # TODO: could read from yml/json
        save_animation=save_animation,
        num_frames_in_animation=num_frames_in_animation,
        plot_width_in_pixels=plot_width_in_pixels,
        plot_height_in_pixels=plot_height_in_pixels,
        output_dir=output_dir)

    animator = PerlinNoiseAnimator(grid, config)

    animator.animate()

    return


def cli():
    parser = ArgumentParser(description=DESCRIPTION)

    parser.add_argument("output_dir", type=str,
                        help="destination directory of saved plots")

    parser.add_argument(
        "--save-animation", action=BooleanOptionalAction, default=False)

    default_plot_width_in_pixels = 2048
    parser.add_argument(
        "-W", "--plot_width_in_pixels",
        type=int,
        help=f" (default: {default_plot_width_in_pixels})",
        default=default_plot_width_in_pixels)

    default_plot_height_in_pixels = 1024
    parser.add_argument(
        "-H", "--plot_height_in_pixels",
        type=int,
        help=f" (default: {default_plot_height_in_pixels})",
        default=default_plot_height_in_pixels)

    default_num_frames_in_animation = 3
    parser.add_argument(
        "-n", "--num_frames_in_animation",
        help=f"default: {default_num_frames_in_animation}",
        type=int,
        default=default_num_frames_in_animation)

    args = parser.parse_args()

    return args


class PerlinNoiseAnimator(OmniSuiteWorldMapAnimator):
    """Animate Perlin noise on a world map."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._latitude_mesh = self._grid.latitude_mesh
        self._longitude_mesh = self._grid.longitude_mesh
        self._perlin_noise_field = zeros_like(self._latitude_mesh)

        # NOTE: could create a new Config class with perlin noise values
        self._spatial_scale = 0.05
        self._temporal_scale = 0.02
        self._seed = 42

        self._mesh = None

        return

    def _plot_initial_frame(self):
        # If you don't initialize the noise field, pcolormesh renders nothing
        self._update_perlin_noise_field(0)

        self._mesh = self._ax.pcolormesh(
            self._grid.longitude,
            self._grid.latitude,
            self._perlin_noise_field,
            transform=self._config.projection,
            cmap="coolwarm"
        )

        return

    def _update_frame(self, frame: int):
        self._update_perlin_noise_field(frame)
        self._mesh.set_array(self._perlin_noise_field.ravel())
        return

    def _update_perlin_noise_field(self, frame: int):
        for i in range(self._perlin_noise_field.shape[0]):
            for j in range(self._perlin_noise_field.shape[1]):
                self._perlin_noise_field[i, j] = pnoise3(
                    self._spatial_scale * self._longitude_mesh[i, j],
                    self._spatial_scale * self._latitude_mesh[i, j],
                    frame * self._temporal_scale,
                    repeatx=360,
                    repeaty=180,
                    base=self._seed)
        return


if __name__ == "__main__":
    main()
