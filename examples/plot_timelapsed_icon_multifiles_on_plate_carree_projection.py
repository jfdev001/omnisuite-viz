from __future__ import annotations

from argparse import (
    ArgumentParser, BooleanOptionalAction, RawTextHelpFormatter)
from dataclasses import dataclass
from matplotlib.pyplot import imread
# from metpy.calc import geopotential_to_height
import netCDF4
import xarray as xarr
from numpy import ndarray
from numpy.ma import MaskedArray
from os import environ
from os.path import abspath, exists
from pathlib import Path
from typing import ClassVar, Dict
from xarray.core.dataset import Variable

from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.animator_config import NetcdfAnimatorConfig
from omnisuite_examples.grid import WorldMapNetcdfGrid
from omnisuite_examples.reader import AbstractReader

DESCRIPTION = """
Save animation frames (and optionally combine the frames to a gif) of
by processing multifile ICON netcdf outputs (e.g., gravity waves, balances).

Illustrates animating data that exists across many files (e.g., loaded in
with xarray) rather than just a single file.

Gravity wave data at: /work/bm1233/m300685/UAICON/modes/inverse/*GWS*
Balance data at : /work/bm1233/m300685/UAICON/modes/inverse/*BAL*

Try looking at December data.
"""


def main():
    # -- begin parse cli --
    args = cli()

    # config args
    save_animation: bool = args.save_animation
    output_dir: str = args.output_dir

    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels

    cmap: str = args.cmap
    alpha: float = args.alpha

    # read args
    netcdf_response_var_file_path: str = args.netcdf_response_var_file_path

    netcdf_response_var_short_name: str = (
        args.netcdf_response_var_short_name)
    blue_marble_path: str = args.blue_marble_path

    # post process args
    use_level_ix: bool = args.use_level_ix
    level_ix: int = args.level_ix
    min_vertical_layer_height_in_meters: float = (
        args.min_vertical_layer_height_in_meters)
    max_vertical_layer_height_in_meters: float = (
        args.max_vertical_layer_height_in_meters)
    # -- end parse cli --

    # read netcdf data, the blue marble image, and post process
    reader = ICONMultifileDataReader(
        netcdf_response_var_file_path=netcdf_response_var_file_path,
        netcdf_response_var_short_name=netcdf_response_var_short_name,
        blue_marble_path=blue_marble_path,
        use_level_ix=use_level_ix,

        level_ix=level_ix,
        min_vertical_layer_height_in_meters=(
            min_vertical_layer_height_in_meters),
        max_vertical_layer_height_in_meters=(
            max_vertical_layer_height_in_meters))

    reader.read()
    reader.postprocess()

    grid = reader.grid
    num_frames_in_animation = grid.response.shape[0]  # equal to n timesteps

    blue_marble_img = reader.blue_marble_img

    # set up plotting configuration
    config = NetcdfAnimatorConfig(
        save_animation=save_animation,
        output_dir=output_dir,
        num_frames_in_animation=num_frames_in_animation,

        coastlines_kwargs={"lw": 0.0},
        plot_height_in_pixels=plot_height_in_pixels,
        plot_width_in_pixels=plot_width_in_pixels,

        netcdf_var_cmap_on_plot=cmap,
        netcdf_var_transparency_on_plot=alpha,


        netcdf_response_var_file_path=netcdf_response_var_file_path,
        blue_marble_path=blue_marble_path)

    # write the frames to disk
    animator = ICONModelAnimator(
        grid=grid, config=config, blue_marble_img=blue_marble_img)

    animator.animate()

    return


@dataclass(kw_only=True)
class ICONConfigConsts:
    LATITUDE_NETCDF_SHORT_VAR_NAME: ClassVar[str] = "lat"
    LONGITUDE_NETCDF_SHORT_VAR_NAME: ClassVar[str] = "lon"
    GEOPOTENTIAL_HEIGHT_NETCDF_SHORT_VAR_NAME: ClassVar[str] = "Z"

    TROPOSPHERE_BEGIN_HEIGHT_IN_METERS: ClassVar[float] = 0
    TROPOSPHERE_END_HEIGHT_IN_METERS: ClassVar[float] = 10_000

    # define expected dimensions
    EXPECTED_LEV: ClassVar[int] = 512
    EXPECTED_LAT_DIM: ClassVar[int] = 512
    EXPECTED_LON_DIM: ClassVar[int] = 1024

    # define axes
    N_RESPONSE_AXES: ClassVar[int] = 4
    RESPONSE_TIME_AXIS: ClassVar[int] = 0
    RESPONSE_LEV_AXIS: ClassVar[int] = 1
    RESPONSE_LAT_AXIS: ClassVar[int] = 2
    RESPONSE_LON_AXIS: ClassVar[int] = 3


def cli():
    parser = ArgumentParser(
        description=DESCRIPTION, formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "output_dir",
        type=str,
        help="destination directory of saved plots")

    parser.add_argument(
        "--save-animation",
        action=BooleanOptionalAction,
        required=True)

    read_group = parser.add_argument_group("read")

    default_netcdf_response_var_file_path = abspath(
        "data/gravity_waves/*.nc")
    read_group.add_argument(
        "--netcdf-response-var-file-path",
        default=default_netcdf_response_var_file_path,
        nargs="+",
        type=str,
        help="path or paths or file glob to netcdf input data."
        f" (default: {default_netcdf_response_var_file_path})")

    default_netcdf_response_var_short_name: str = "u"
    read_group.add_argument(
        "--netcdf-response-var-short-name",
        help="short name of variable to plot over time"
        f" (default: {default_netcdf_response_var_short_name})",
        type=str,
        default=default_netcdf_response_var_short_name)

    read_group.add_argument(
        "--use-level-ix",
        help="flag to use --level-ix directly if true, otherwise"
        " compute an average of response variable over some region of the"
        " atmosphere defined by --min-vertical-layer-height-in-meters"
        " and --max-vertical-layer-height-in-meters.",
        action=BooleanOptionalAction,
        default=True)

    default_level_ix = 72  # based on conversation with P. Ghosh
    read_group.add_argument(
        "--level-ix",
        type=int,
        help="the level at which to plot the ICON data."
        f" (default: {default_level_ix})",
        default=default_level_ix
    )

    default_min_vertical_layer_height_in_meters = (
        ICONConfigConsts.TROPOSPHERE_BEGIN_HEIGHT_IN_METERS)
    read_group.add_argument(
        "--min-vertical-layer-height-in-meters",
        type=float,
        help="The lower bound in meters of the layer you wish to plot."
        f" (default: {default_min_vertical_layer_height_in_meters})",
        default=default_min_vertical_layer_height_in_meters)

    default_max_vertical_layer_height_in_meters = (
        ICONConfigConsts.TROPOSPHERE_END_HEIGHT_IN_METERS)
    read_group.add_argument(
        "--max-vertical-layer-height-in-meters",
        type=float,
        help="The upper bound in meters of the layer you wish to plot."
        f" (default: {default_max_vertical_layer_height_in_meters})",
        default=default_max_vertical_layer_height_in_meters)

    default_blue_marble_path = Path(
        f"{environ['HOME']}/.cartopy_backgrounds/BlueMarble_3600x1800.png")
    read_group.add_argument(
        "--blue-marble-path",
        type=str,
        help=f"path to blue marble PNG. (default: {default_blue_marble_path})",
        default=default_blue_marble_path)

    config_group = parser.add_argument_group("config")

    default_plot_width_in_pixels = 2048
    config_group.add_argument(
        "-W", "--plot_width_in_pixels",
        type=int,
        help=f" (default: {default_plot_width_in_pixels})",
        default=default_plot_width_in_pixels)

    default_plot_height_in_pixels = 1024
    config_group.add_argument(
        "-H", "--plot_height_in_pixels",
        type=int,
        help=f" (default: {default_plot_height_in_pixels})",
        default=default_plot_height_in_pixels)

    default_alpha = 0.3
    config_group.add_argument(
        "--alpha",
        help=f"transparency. (default: {default_alpha})",
        type=float,
        default=default_alpha)

    default_cmap = "bwr"
    config_group.add_argument(
        "--cmap",
        help=f"mpl color map string (default: {default_cmap})",
        type=str,
        default=default_cmap)

    args = parser.parse_args()
    return args


class ICONMultifileDataReader(AbstractReader):
    """Read and postprocess multifile ICON data (e.g., gravity wave)."""

    def __init__(
        self,
        netcdf_response_var_file_path: str,
        netcdf_response_var_short_name: str,
        blue_marble_path: str,
        use_level_ix: bool,
        level_ix: int = 0,
        min_vertical_layer_height_in_meters: float = (
            ICONConfigConsts.TROPOSPHERE_BEGIN_HEIGHT_IN_METERS),
        max_vertical_layer_height_in_meters: float = (
            ICONConfigConsts.TROPOSPHERE_END_HEIGHT_IN_METERS)):

        # TODO: keep public for now
        self.netcdf_response_var_file_path = netcdf_response_var_file_path
        self.netcdf_response_var_short_name = (
            netcdf_response_var_short_name)
        self.blue_marble_path = blue_marble_path
        self.use_level_ix = use_level_ix
        self.level_ix = level_ix

        self.min_vertical_layer_height_in_meters = (
            min_vertical_layer_height_in_meters)
        self.max_vertical_layer_height_in_meters = (
            max_vertical_layer_height_in_meters)

        # TODO: make property?
        self.blue_marble_img = None
        return

    def read(self):
        self.mfdataset = xarr.open_mfdataset(
            self.netcdf_response_var_file_path)

        # TODO: this is not memory efficient because it gathers the
        # chunked data into a single numpy array
        self.response = (
            self.mfdataset
            .variables
            .get(self.netcdf_response_var_short_name)
            .values)

        self.latitude = (
            self.mfdataset
            .variables
            .get(ICONConfigConsts.LATITUDE_NETCDF_SHORT_VAR_NAME)
            .values)

        self.longitude = (
            self.mfdataset
            .variables
            .get(ICONConfigConsts.LONGITUDE_NETCDF_SHORT_VAR_NAME)
            .values)

        self.geopotential_height = (
            self.mfdataset
            .variables
            .get(ICONConfigConsts.GEOPOTENTIAL_HEIGHT_NETCDF_SHORT_VAR_NAME)
            .values)

        # for plotting blue marble in animator (note: move elsewhere??)
        self.blue_marble_img = imread(self.blue_marble_path)

        return

    def postprocess(self):
        if self.use_level_ix:
            self.response = self.response[:, self.level_ix, :, :]
        else:
            raise NotImplementedError(
                "Uncertain how to get geometric height from fields in netdcf."
                " Discussion with P. Ghosh on earlier problem indicates that"
                " that /work/bm1233/b383395/icon-visualization-examples/scripts/modes_GWsDensity_032019_climatology_test.py"
                " contains the generalized height and sigma map 1:1")
            # TODO: move to utils func
            # TODO: you need to use geopotential to height here
            # Use the upper and lower bounds of height to average response var...
            # thus converting 4th order tensor to 3rd order tensor for plotting..
            # this requires determining the index of the upper and lower bounds!
            height_mean = self.height.mean(
                axis=(
                    ICONConfigConsts.HEIGHT_LAT_AXIS,
                    ICONConfigConsts.HEIGHT_LON_AXIS))

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

            # Height variable has values in decreasing order
            # i.e., height[0] = 140_000, height[1] = 135_000, etc
            # so to slice correctly you must slice max vertical height ix
            # TO min vertical height index
            assert self._is_monotonically_decreasing(height_mean)
            layer_slice = slice(
                max_vertical_layer_height_in_meters_ix,
                min_vertical_layer_height_in_meters_ix+1)

            response = self.response[:, layer_slice, :, :]
            self.response: ndarray = response.mean(
                axis=ICONConfigConsts.RESPONSE_HEIGHT_AXIS)
        return

    @staticmethod
    def _is_monotonically_decreasing(arr: ndarray):
        assert len(arr.shape) == 1
        n = arr.shape[0]
        return ((arr[0:n-1] - arr[1:n]) > 0).all()

    @staticmethod
    def _absolute_difference(mask_arr1: MaskedArray, mask_arr2: MaskedArray):
        return (mask_arr1 - mask_arr2).__abs__()

    @property
    def grid(self) -> WorldMapNetcdfGrid:
        # TODO: make sense to construct grid here??
        grid = WorldMapNetcdfGrid(
            self.response,
            self.latitude,
            self.longitude
        )
        return grid

    def __del__(self):
        self.mfdataset.close()
        return


class ICONModelAnimator(OmniSuiteWorldMapAnimator):
    def __init__(self, grid, config, blue_marble_img):
        """ 
        TODO: Ugly constructor??
        """
        super().__init__(grid, config)
        self._grid: WorldMapNetcdfGrid
        self._config: NetcdfAnimatorConfig
        self._blue_marble_img = blue_marble_img
        return

    def _plot_initial_frame(self):
        # Plot an actual image of the Earth
        self._ax.imshow(
            self._blue_marble_img,
            extent=self._config.blue_marble_extent,
            transform=self._config.transform,
            zorder=1,)

        # Overlay the image of the Earth with your data of interest
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
        # Update frame with the value of the response variable at next
        # frame where frame == timestep (e.g., 12 timesteps, 12 frames)
        response_at_time = self._grid.response[frame]
        self._mesh.set_array(response_at_time)
        return


if __name__ == "__main__":
    main()
