from __future__ import annotations

from argparse import ArgumentParser, BooleanOptionalAction, RawTextHelpFormatter
from dataclasses import dataclass
from matplotlib.pyplot import imread
from netCDF4 import Dataset
from numpy import ndarray
from os import environ
from os.path import abspath
from pathlib import Path
from typing import ClassVar, Dict

from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.grid import WorldMapNetcdfGrid
from omnisuite_examples.animator_config import NetcdfAnimatorConfig

DESCRIPTION = """
Save animation frames (and optionally combine the frames to a gif) of
netcdf outputs from an ICON simulation on Plate-Carree projection.

Since ICON height files specify the altitude of a simulation output
typically with 180 sampling points, the user specifies the lower and
upper bounds of the altitude they wish to plot and an average on the response
variable of interest over this vertical region is taken. As an example,
consider the troposphere exists roughly between altitudes of 0 and 10_000
meters. Providing these as lower and upper bounds will mean that an average
of a response variable (e.g., zonal wind) will be taken and then plotted
on the Plate-Carree projection.
"""


def main():
    # cli
    args = cli()

    save_animation: bool = args.save_animation
    output_dir: str = args.output_dir

    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels

    netcdf_response_var_file_path: str = args.netcdf_response_var_file_path
    netcdf_long_name_of_response_var: str = (
        args.netcdf_long_name_of_response_var)

    netcdf_height_file_path: str = args.netcdf_height_file_path
    netcdf_long_name_of_height_var: str = args.netcdf_long_name_of_height_var

    blue_marble_path: str = args.blue_marble_path

    cmap: str = args.cmap

    alpha: float = args.alpha

    config = ICONModelAnimatorConfig(
        save_animation=save_animation,
        output_dir=output_dir,

        plot_height_in_pixels=plot_height_in_pixels,
        plot_width_in_pixels=plot_width_in_pixels,

        blue_marble_path=blue_marble_path,

        netcdf_response_var_file_path=netcdf_response_var_file_path,
        netcdf_long_name_of_response_var=netcdf_long_name_of_response_var,
        netcdf_var_cmap_on_plot=cmap,
        netcdf_var_transparency_on_plot=alpha,

        netcdf_height_file_path=netcdf_height_file_path,
        netcdf_long_name_of_height_var=netcdf_long_name_of_height_var
    )

    # grid = ICONModelGrid(latitude=config.latitude, longitude=config.longitude)

    # animator = ICONModelAnimator(grid=grid, config=config)
    # animator.animate()

    return


def cli():
    parser = ArgumentParser(
        description=DESCRIPTION, formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "output_dir",
        type=str,
        help="destination directory of saved plots")

    default_netcdf_response_var_file_path = abspath(
        "data/R2B7_free_30_years/R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc")
    parser.add_argument(
        "--netcdf-response-var-file-path",
        default=default_netcdf_response_var_file_path,
        type=str,
        help="path to netcdf input data from ICON simulation."
        f" (default: {default_netcdf_response_var_file_path})")

    default_netcdf_long_name_of_response_var: str = "Zonal wind"
    parser.add_argument(
        "--netcdf-long-name-of-response-var",
        help="long name of variable to plot over time"
        f" (default: {default_netcdf_long_name_of_response_var})",
        type=str,
        default=default_netcdf_long_name_of_response_var)

    default_netcdf_height_file_path = abspath(
        "data/R2B7_free_30_years/hfile.nc")
    parser.add_argument(
        "---netcdf-height-file-path",
        default=default_netcdf_height_file_path,
        type=str,
        help="path to netcdf height file data for ICON simulation."
        f" (default: {default_netcdf_height_file_path})")

    default_netcdf_long_name_of_height_var: str = (
        "geometric height at full level center")
    parser.add_argument(
        "--netcdf-long-name-of-height-var",
        help="long name of variable for vertical level."
        f" (default: {default_netcdf_long_name_of_height_var})",
        type=str,
        default=default_netcdf_long_name_of_height_var)

    default_blue_marble_path = Path(
        f"{environ['HOME']}/.cartopy_backgrounds/BlueMarble_3600x1800.png")
    parser.add_argument(
        "--blue-marble-path",
        type=str,
        help=f"path to blue marble PNG. (default: {default_blue_marble_path})",
        default=default_blue_marble_path)

    default_begin_vertical_layer_in_meters = 0
    parser.add_argument(
        "--begin-vertical-layer-in-meters",
        type=int,
        help="The lower bound in meters of the layer you wish to plot."
        f" (default: {default_begin_vertical_layer_in_meters})",
        default=default_begin_vertical_layer_in_meters)

    default_end_vertical_layer_in_meters = 10_000
    parser.add_argument(
        "--end-vertical-layer-in-meters",
        type=int,
        help="The upper bound in meters of the layer you wish to plot."
        f" (default: {default_end_vertical_layer_in_meters})",
        default=default_begin_vertical_layer_in_meters)

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


class ICONModelGrid(WorldMapNetcdfGrid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return


@dataclass(kw_only=True)
class ICONModelAnimatorConfig(NetcdfAnimatorConfig):
    TROPOSPHERE_BEGIN_HEIGHT_IN_METERS: ClassVar[float] = 0
    TROPOSPHERE_END_HEIGHT_IN_METERS: ClassVar[float] = 10_000

    netcdf_height_file_path: str
    netcdf_long_name_of_height_var: str = (
        "geometric height at full level center")
    min_height_in_meters_for_vertical_layer: float = (
        TROPOSPHERE_END_HEIGHT_IN_METERS)
    max_height_in_meters_for_vertical_layer: float = (
        TROPOSPHERE_END_HEIGHT_IN_METERS)

    def __post_init__(self):
        super().__post_init__()
        # load datasets and define variable name maps
        self._netcdf_response_var_file = Dataset(
            self.netcdf_response_var_file_path)
        self._netcdf_height_file = Dataset(self.netcdf_height_file_path)

        netcdf_var_name_to_response_variable = (
            self._netcdf_response_var_file.variables)
        netcdf_var_name_to_height_variable = self._netcdf_height_file.variables

        netcdf_long_name_to_netcdf_response_var_name = (
            self._get_netcdf_long_name_to_netcdf_var_name(
                self._netcdf_response_var_file))

        netcdf_long_name_to_netcdf_height_var_name = (
            self._get_netcdf_long_name_to_netcdf_var_name(
                self._netcdf_height_file))

        # define expected dimensions
        expected_height_2_dim = 180  # vertical levels from n45 remap
        expected_height_dim = expected_height_2_dim
        expected_lat_dim = 90
        expected_lon_dim = 180
        expected_time_dim = 12  # months

        # load height variable
        netcdf_height_var_name = netcdf_long_name_to_netcdf_height_var_name[
            self.netcdf_long_name_of_height_var]
        height_variable = netcdf_var_name_to_height_variable[
            netcdf_height_var_name]

        self.height: ndarray = height_variable[:]
        assert len(self.height.shape) == 3, \
            "expected dims: (height_2, lat, lon)"
        assert self.height.shape[0] == expected_height_2_dim
        assert self.height.shape[1] == expected_lat_dim
        assert self.height.shape[2] == expected_lon_dim

        #
        # load output variable data
        #
        netcdf_response_var_name = (
            netcdf_long_name_to_netcdf_response_var_name[
                self.netcdf_long_name_of_response_var])
        response_variable = netcdf_var_name_to_response_variable[
            netcdf_response_var_name]
        self.response: ndarray = response_variable[:]
        assert len(self.response.shape) == 4, (
            "expected dims: (time, height, lat, lon)")
        assert self.response.shape[0] == expected_time_dim
        assert self.response.shape[1] == expected_height_dim
        assert self.response.shape[2] == expected_lat_dim
        assert self.response.shape[3] == expected_lon_dim

        self.latitude: ndarray = netcdf_var_name_to_response_variable[
            self.LATITUDE_NETCDF_VAR_NAME][:]
        assert (
            len(self.latitude.shape) == 1
            and self.latitude.shape[0] == expected_lat_dim)

        self.longitude: ndarray = netcdf_var_name_to_response_variable[
            self.LONGITUDE_NETCDF_VAR_NAME][:]
        assert (
            len(self.longitude.shape) == 1
            and self.longitude.shape[0] == expected_lon_dim)

        # TODO: use the upper and lower bounds of height to average what
        # to convert the 4th order tensor to 3rd order tensor for plotting
        pass

        # TODO: load blue marble... should probably do this in animator?
        self.blue_marble_img = imread(self.blue_marble_path)

        return

    def _get_netcdf_long_name_to_netcdf_var_name(
            self, dataset: Dataset) -> Dict:
        variables = dataset.variables
        netcdf_long_name_to_netcdf_var_name = {
            getattr(variables[var], 'long_name', var): var
            for var in variables.keys()}
        return netcdf_long_name_to_netcdf_var_name

    def __del__(self):
        self._netcdf_response_var_file.close()
        self._netcdf_height_file.close()
        return


class ICONModelAnimator(OmniSuiteWorldMapAnimator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

    def _plot_initial_frame(self):
        raise

    def _update_frame(self, frame: int):
        raise


if __name__ == "__main__":
    main()
