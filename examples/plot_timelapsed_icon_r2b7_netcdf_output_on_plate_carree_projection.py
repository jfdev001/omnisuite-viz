from __future__ import annotations

from argparse import (
    ArgumentParser, BooleanOptionalAction, RawTextHelpFormatter)
from dataclasses import dataclass
from matplotlib.pyplot import imread
from netCDF4 import Dataset
from numpy import ndarray
from numpy.ma import MaskedArray
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

Since ICON height files specify the altitude of a simulation output, 
the user specifies the lower and upper bounds for the altitude (height)
and an average of the response variable of interest over this vertical 
region is taken. As an example, consider the troposphere exists roughly between 
altitudes of 0 and 10_000 meters. Providing these as lower and upper bounds 
will mean that an average of a response variable (e.g., zonal wind) will be 
taken and then plotted on the Plate-Carree projection.
"""


def main():
    # parse cli args
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

    min_vertical_layer_height_in_meters: float = (
        args.min_vertical_layer_height_in_meters)
    max_vertical_layer_height_in_meters: float = (
        args.max_vertical_layer_height_in_meters)

    cmap: str = args.cmap
    alpha: float = args.alpha

    config = ICONModelAnimatorConfig(
        save_animation=save_animation,
        output_dir=output_dir,

        coastlines_kwargs={"lw": 0.0},

        plot_height_in_pixels=plot_height_in_pixels,
        plot_width_in_pixels=plot_width_in_pixels,

        blue_marble_path=blue_marble_path,

        netcdf_response_var_file_path=netcdf_response_var_file_path,
        netcdf_long_name_of_response_var=netcdf_long_name_of_response_var,
        netcdf_var_cmap_on_plot=cmap,
        netcdf_var_transparency_on_plot=alpha,

        netcdf_height_file_path=netcdf_height_file_path,
        netcdf_long_name_of_height_var=netcdf_long_name_of_height_var,

        min_vertical_layer_height_in_meters=min_vertical_layer_height_in_meters,
        max_vertical_layer_height_in_meters=max_vertical_layer_height_in_meters
    )

    response = config.response_mean_in_atmospheric_layer
    latitude = config.latitude
    longitude = config.longitude
    grid = WorldMapNetcdfGrid(
        response=response,
        latitude=latitude,
        longitude=longitude)

    animator = ICONModelAnimator(grid=grid, config=config)
    animator.animate()

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

    default_max_vertical_layer_height_in_meters = 0
    parser.add_argument(
        "--max-vertical-layer-height-in-meters",
        type=float,
        help="The lower bound in meters of the layer you wish to plot."
        f" (default: {default_max_vertical_layer_height_in_meters})",
        default=default_max_vertical_layer_height_in_meters)

    default_min_vertical_layer_height_in_meters = 10_000
    parser.add_argument(
        "--min-vertical-layer-height-in-meters",
        type=float,
        help="The upper bound in meters of the layer you wish to plot."
        f" (default: {default_min_vertical_layer_height_in_meters})",
        default=default_max_vertical_layer_height_in_meters)

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


class ICONModelAnimator(OmniSuiteWorldMapAnimator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grid: WorldMapNetcdfGrid
        self._config: ICONModelAnimatorConfig
        return

    def _plot_initial_frame(self):
        self._ax.imshow(
            self._config.blue_marble_img,
            extent=self._config.blue_marble_extent,
            transform=self._config.transform,
            zorder=1,)

        t0 = 0
        self._mesh = self._ax.pcolormesh(
            self._grid.longitude,
            self._grid.latitude,
            self._grid.response[t0],
            zorder=2,  # must have for data plotted "on top of" blue marble
            antialiased=True,
            transform=self._config.transform,
            alpha=self._config.netcdf_var_transparency_on_plot,
            cmap=self._config.netcdf_var_cmap_on_plot)

        return

    def _update_frame(self, frame: int):
        response_at_time = self._grid.response[frame]
        self._mesh.set_array(response_at_time)
        return


@dataclass(kw_only=True)
class ICONConfigConsts:
    TROPOSPHERE_BEGIN_HEIGHT_IN_METERS: ClassVar[float] = 0
    TROPOSPHERE_END_HEIGHT_IN_METERS: ClassVar[float] = 10_000

    EXPECTED_HEIGHT_2_DIM: ClassVar[int] = 180  # vert levels from F45 remap
    EXPECTED_HEIGHT_DIM: ClassVar[int] = EXPECTED_HEIGHT_2_DIM
    EXPECTED_LAT_DIM: ClassVar[int] = 90
    EXPECTED_LON_DIM: ClassVar[int] = 180
    EXPECTED_TIME_DIM: ClassVar[int] = 12  # months in a year

    N_HEIGHT_AXES: ClassVar[int] = 3
    HEIGHT_HEIGHT_AXIS: ClassVar[int] = 0
    HEIGHT_LAT_AXIS: ClassVar[int] = 1
    HEIGHT_LON_AXIS: ClassVar[int] = 2

    N_RESPONSE_AXES: ClassVar[int] = 4
    RESPONSE_TIME_AXIS: ClassVar[int] = 0
    RESPONSE_HEIGHT_AXIS: ClassVar[int] = 1
    RESPONSE_LAT_AXIS: ClassVar[int] = 2
    RESPONSE_LON_AXIS: ClassVar[int] = 3


@dataclass(kw_only=True)
class ICONModelAnimatorConfig(NetcdfAnimatorConfig):

    netcdf_height_file_path: str
    netcdf_long_name_of_height_var: str = (
        "geometric height at full level center")
    min_vertical_layer_height_in_meters: float = (
        ICONConfigConsts.TROPOSPHERE_END_HEIGHT_IN_METERS)
    max_vertical_layer_height_in_meters: float = (
        ICONConfigConsts.TROPOSPHERE_END_HEIGHT_IN_METERS)

    def __post_init__(self):
        # TODO: doing too much and side effects...

        super().__post_init__()
        # load datasets and define variable name maps
        self._netcdf_response_var_file = Dataset(
            self.netcdf_response_var_file_path)
        netcdf_var_name_to_response_variable = (
            self._netcdf_response_var_file.variables)
        netcdf_long_name_to_netcdf_response_var_name = (
            self._get_netcdf_long_name_to_netcdf_var_name(
                self._netcdf_response_var_file))

        self._netcdf_height_file = Dataset(self.netcdf_height_file_path)
        netcdf_var_name_to_height_variable = self._netcdf_height_file.variables
        netcdf_long_name_to_netcdf_height_var_name = (
            self._get_netcdf_long_name_to_netcdf_var_name(
                self._netcdf_height_file))

        # load time variable and set number of frames in animation
        time = self._netcdf_response_var_file.variables[
            self.TIME_NETCDF_VAR_NAME]
        n_times = time.shape[0]
        self.num_frames_in_animation = n_times

        # load height variable
        netcdf_height_var_name = netcdf_long_name_to_netcdf_height_var_name[
            self.netcdf_long_name_of_height_var]
        height_variable = netcdf_var_name_to_height_variable[
            netcdf_height_var_name]
        height: ndarray = height_variable[:]

        assert len(height.shape) == ICONConfigConsts.N_HEIGHT_AXES, (
            "expected dims: (height_2, lat, lon)")
        assert (height.shape[ICONConfigConsts.HEIGHT_HEIGHT_AXIS]
                == ICONConfigConsts.EXPECTED_HEIGHT_2_DIM)
        assert (height.shape[ICONConfigConsts.HEIGHT_LAT_AXIS]
                == ICONConfigConsts.EXPECTED_LAT_DIM)
        assert (height.shape[ICONConfigConsts.HEIGHT_LON_AXIS]
                == ICONConfigConsts.EXPECTED_LON_DIM)

        # load output variable data
        netcdf_response_var_name = (
            netcdf_long_name_to_netcdf_response_var_name[
                self.netcdf_long_name_of_response_var])
        response_variable = netcdf_var_name_to_response_variable[
            netcdf_response_var_name]
        response: ndarray = response_variable[:]

        assert len(response.shape) == ICONConfigConsts.N_RESPONSE_AXES, (
            "expected dims: (time, height, lat, lon)")
        assert (response.shape[ICONConfigConsts.RESPONSE_TIME_AXIS] ==
                ICONConfigConsts.EXPECTED_TIME_DIM)
        assert (response.shape[ICONConfigConsts.RESPONSE_HEIGHT_AXIS] ==
                ICONConfigConsts.EXPECTED_HEIGHT_DIM)
        assert (response.shape[ICONConfigConsts.RESPONSE_LAT_AXIS] ==
                ICONConfigConsts.EXPECTED_LAT_DIM)
        assert (response.shape[ICONConfigConsts.RESPONSE_LON_AXIS] ==
                ICONConfigConsts.EXPECTED_LON_DIM)

        self.latitude: ndarray = netcdf_var_name_to_response_variable[
            self.LATITUDE_NETCDF_VAR_NAME][:]
        assert (
            len(self.latitude.shape) == 1
            and self.latitude.shape[0] == ICONConfigConsts.EXPECTED_LAT_DIM)

        self.longitude: ndarray = netcdf_var_name_to_response_variable[
            self.LONGITUDE_NETCDF_VAR_NAME][:]
        assert (
            len(self.longitude.shape) == 1
            and self.longitude.shape[0] == ICONConfigConsts.EXPECTED_LON_DIM)

        # Use the upper and lower bounds of height to average response var...
        # thus converting 4th order tensor to 3rd order tensor for plotting..
        # this requires determining the index of the upper and lower bounds!
        height_mean = height.mean(
            axis=(
                ICONConfigConsts.HEIGHT_LAT_AXIS,
                ICONConfigConsts.HEIGHT_LON_AXIS))
        assert self._is_monotonically_decreasing(height_mean)

        assert (
            self.min_vertical_layer_height_in_meters
            <= self.max_vertical_layer_height_in_meters), (
            "`min_vertical_layer_height_in_meters` must be less than or equal"
            " `max_vertical_layer_height_in_meters`. E.g., if you desire"
            " an average of a reponse variable in the troposphere, you would"
            " provide 0 and 10_000 meters, respectively. Providing a lower"
            " bound for a layer of interest that is greater than the upper"
            " bound is non-physical."
            " (e.g., `max_vertical_layer_height_in_meters ="
            f" {self.max_vertical_layer_height_in_meters}` and"
            " `min_vertical_layer_height_in_meters = "
            f" {self.min_vertical_layer_height_in_meters}` is non-physical.")

        min_vertical_layer_height_abs_diff_height_mean = (
            self._absolute_difference(
                height_mean, self.min_vertical_layer_height_in_meters))
        min_vertical_layer_height_in_meters_ix = (
            min_vertical_layer_height_abs_diff_height_mean.argmin())

        max_vertical_layer_height_abs_diff_height_mean = (
            self._absolute_difference(
                height_mean, self.max_vertical_layer_height_in_meters))
        max_vertical_layer_height_in_meters_ix = (
            max_vertical_layer_height_abs_diff_height_mean.argmin())

        layer_slice = slice(
            max_vertical_layer_height_in_meters_ix,
            min_vertical_layer_height_in_meters_ix+1)
        response = response[:, layer_slice, :, :]
        self.response_mean_in_atmospheric_layer: ndarray = response.mean(
            axis=ICONConfigConsts.RESPONSE_HEIGHT_AXIS)

        # for plotting blue marble in animator (note: move elsewhere??)
        self.blue_marble_img = imread(self.blue_marble_path)

        return

    @staticmethod
    def _get_netcdf_long_name_to_netcdf_var_name(dataset: Dataset) -> Dict:
        variables = dataset.variables
        netcdf_long_name_to_netcdf_var_name = {
            getattr(variables[var], 'long_name', var): var
            for var in variables.keys()}
        return netcdf_long_name_to_netcdf_var_name

    @staticmethod
    def _is_monotonically_decreasing(arr: ndarray):
        assert len(arr.shape) == 1
        n = arr.shape[0]
        return ((arr[0:n-1] - arr[1:n]) > 0).all()

    @staticmethod
    def _absolute_difference(mask_arr1: MaskedArray, mask_arr2: MaskedArray):
        return (mask_arr1 - mask_arr2).__abs__()

    def __del__(self):
        self._netcdf_response_var_file.close()
        self._netcdf_height_file.close()
        return


if __name__ == "__main__":
    main()
