from argparse import ArgumentParser, BooleanOptionalAction
from dataclasses import dataclass
from matplotlib.pyplot import imread, show
from netCDF4 import Dataset
from numpy import ndarray
from os import environ
from os.path import exists, abspath
from pathlib import Path
from typing import ClassVar

from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.animator_config import OmniSuiteAnimatorConfig
from omnisuite_examples.grid import WorldMapGrid

DESCRIPTION = """
Save animation frames (and optionally combine the frames to a gif) of
netcdf outputs from SpeedyWeather.jl on Plate-Carree projection.
"""


def main():
    # cli
    args = cli()
    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels
    save_animation: bool = args.save_animation
    output_dir: str = args.output_dir
    netcdf_file_path: str = args.netcdf_file_path
    netcdf_long_name_of_var_to_plot: str = args.netcdf_long_name_of_var_to_plot
    blue_marble_path: str = args.blue_marble_path
    vertical_layer: int = args.vertical_layer

    # grid
    grid = WorldMapGrid()

    # config
    config = SpeedyWeatherAnimatorConfig(
        save_animation=save_animation,
        output_dir=output_dir,
        netcdf_file_path=netcdf_file_path,
        netcdf_long_name_of_var_to_plot=netcdf_long_name_of_var_to_plot,
        plot_width_in_pixels=plot_width_in_pixels,
        plot_height_in_pixels=plot_height_in_pixels,
        coastlines_kwargs={"lw": 0.0},
        blue_marble_path=blue_marble_path,
        vertical_layer=vertical_layer)

    # animator
    animator = SpeedyWeatherAnimator(grid=grid, config=config)

    animator.animate()
    pass


def cli():
    parser = ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        "output_dir",
        type=str,
        help="destination directory of saved plots")

    default_netcdf_file_path = abspath("data/output.nc")
    parser.add_argument(
        "--netcdf-file-path",
        default=default_netcdf_file_path,
        type=str,
        help="path to netcdf input data from SpeedyWeather.jl simulation."
        f" (default: {default_netcdf_file_path})")

    default_blue_marble_path = Path(
        f"{environ['HOME']}/.cartopy_backgrounds/BlueMarble_3600x1800.png")
    parser.add_argument(
        "--blue-marble-path",
        type=str,
        help=f"path to blue marble PNG. (default: {default_blue_marble_path})",
        default=default_blue_marble_path)

    default_long_name: str = "zonal wind"
    parser.add_argument(
        "--netcdf-long-name-of-var-to-plot",
        help="long name of variable to plot over time"
        f" (default: {default_long_name})",
        type=str,
        default=default_long_name)

    default_vertical_layer = 15
    parser.add_argument(
        "--vertical-layer",
        type=int,
        help="vertical layer of 3D model to plot"
        f" (default: {default_vertical_layer})",
        default=default_vertical_layer)

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

    default_alpha = 0.3
    parser.add_argument(
        "--alpha",
        help=f"transparency. (default: {default_alpha})",
        type=float,
        default=default_alpha)

    default_cmap = "bwr"
    parser.add_argument(
        "--cmap",
        help=f"mpl color map string (default: {default_cmap})",
        type=str,
        default=default_cmap)

    args = parser.parse_args()
    return args


class SpeedyWeatherAnimator(OmniSuiteWorldMapAnimator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._config: SpeedyWeatherAnimatorConfig  # TODO: crude type hinting

        variables = self._config.ncfile.variables

        self._lon: ndarray = variables[
            self._config.LONGITUDE_NETCDF_VAR_NAME][:]

        self._lat: ndarray = variables[
            self._config.LATITUDE_NETCDF_VAR_NAME][:]

        self._time_to_layer_lat_to_lon_to_var_output: ndarray = variables[
            self._config.netcdf_output_var_name][:]

        self._time_to_lat_to_lon_to_var_output_at_layer: ndarray = \
            self._time_to_layer_lat_to_lon_to_var_output[
                :, self._config.vertical_layer - 1, :]

        self._mesh = None

        return

    def _plot_initial_frame(self):

        self._ax.imshow(
            self._config.blue_marble_img,
            extent=self._config.blue_marble_extent,
            transform=self._config.transform,
            zorder=1,)

        self._mesh = self._ax.pcolormesh(
            self._lon,  # TODO: ordering here??
            self._lat,
            self._time_to_lat_to_lon_to_var_output_at_layer[0],
            zorder=2,  # must have for data plotted "on top of" blue marble
            antialiased=True,
            transform=self._config.transform,
            alpha=self._config.alpha,
            cmap=self._config.cmap,)

        return

    def _update_frame(self, frame: int):
        lat_to_lon_to_var_output_at_time_at_layer =\
            self._time_to_lat_to_lon_to_var_output_at_layer[frame]
        self._mesh.set_array(lat_to_lon_to_var_output_at_time_at_layer)
        return


@dataclass(kw_only=True)
class SpeedyWeatherAnimatorConfig(OmniSuiteAnimatorConfig):
    LATITUDE_NETCDF_VAR_NAME: ClassVar[str] = "lat"
    LONGITUDE_NETCDF_VAR_NAME: ClassVar[str] = "lon"
    TIME_NETCDF_VAR_NAME: ClassVar[str] = "time"

    netcdf_file_path: str

    blue_marble_path: str
    blue_marble_extent = (-180, 180, -90, 90)  # full blue marble

    vertical_layer: int

    netcdf_long_name_of_var_to_plot: str = "zonal wind"

    alpha: float = 0.30
    cmap: str = "bwr"

    def __post_init__(self):
        super().__post_init__()
        assert exists(self.netcdf_file_path), \
            "You can download an example NetCDF file from" +\
            " https://zenodo.org/records/15639060"
        assert exists(self.blue_marble_path)

        # Load the netcdf data you need for plotting 
        # NOTE: side effects... and doing work? bad design...
        self.ncfile = Dataset(self.netcdf_file_path)
        n_times = self.ncfile.variables[self.TIME_NETCDF_VAR_NAME].shape[0]
        self.num_frames_in_animation = n_times

        netcdf_long_name_to_netcdf_var_name = {
            self.ncfile.variables[var].long_name: var
            for var in self.ncfile.variables.keys()}

        self.netcdf_output_var_name = netcdf_long_name_to_netcdf_var_name[
            self.netcdf_long_name_of_var_to_plot]

        self.blue_marble_img = imread(self.blue_marble_path)

        return

    def __del__(self):
        self.ncfile.close()
        return


if __name__ == "__main__":
    main()
