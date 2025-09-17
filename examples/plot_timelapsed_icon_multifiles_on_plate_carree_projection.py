from __future__ import annotations

from argparse import (
    ArgumentParser, BooleanOptionalAction, RawTextHelpFormatter)
from dataclasses import dataclass
from os import environ
from pathlib import Path
from time import time as time_in_seconds
from typing import ClassVar

from cdo import Cdo
from numpy import ndarray
import numpy as np
import xarray as xarr
import netCDF4
from matplotlib.pyplot import imread
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from omnisuite_viz.reader import AbstractReader
from omnisuite_viz.grid import WorldMapNetcdfGrid
from omnisuite_viz.animator_config import NetcdfAnimatorConfig
from omnisuite_viz.animator import OmniSuiteWorldMapAnimator


SECONDS_PER_MINUTE: int = 60


DESCRIPTION = """
Save animation frames (and optionally combine the frames to a gif)
by processing multifile ICON netcdf outputs (e.g., gravity waves, balances).

Illustrates animating data that exists across many files (e.g., loaded in
with xarray) rather than just a single file.

See `tests/exploratory/run_gravity_wave_example` or
`tests/exploratory/run_bal_example` for animation outputs on Levante.
"""


def main():
    # -- begin parse cli --
    args = cli()

    # load cdo after parsing for faster --help
    print("Loading CDO...")
    global cdo
    cdo = Cdo()

    # config args
    save_animation: bool = args.save_animation
    output_dir: str = args.output_dir

    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels

    cmap: str = args.cmap
    alpha: float = args.alpha

    # read args
    netcdf_response_var_file_path: list[str] = (
        args.netcdf_response_var_file_path)

    netcdf_response_var_short_name: str = (
        args.netcdf_response_var_short_name)
    blue_marble_path: str = args.blue_marble_path

    concat_dim: str = args.concat_dim

    show_timestamp: bool = args.show_timestamp
    time_delta_in_hours_between_consecutive_files: int = (
        args.time_delta_in_hours_between_consecutive_files)
    timestamp_x_pos = args.timestamp_x_pos
    timestamp_y_pos = args.timestamp_y_pos

    show_colorbar: bool = args.show_colorbar

    mask_threshold_abs_value: float = args.mask_threshold_abs_value

    level_ix: int = args.level_ix
    # -- end parse cli --

    # read netcdf data, the blue marble image, and post process
    reader = ICONMultifileDataReader(
        netcdf_response_var_file_path=netcdf_response_var_file_path,
        netcdf_response_var_short_name=netcdf_response_var_short_name,
        blue_marble_path=blue_marble_path,

        concat_dim=concat_dim,

        show_timestamp=show_timestamp,
        time_delta_in_hours_between_consecutive_files=time_delta_in_hours_between_consecutive_files,

        level_ix=level_ix)

    print("Reading data...")
    start_read = time_in_seconds()
    reader.read()
    end_read = time_in_seconds()
    elapsed_read = end_read - start_read
    read_time_in_minutes = int(elapsed_read // SECONDS_PER_MINUTE)
    read_time_in_seconds = elapsed_read % SECONDS_PER_MINUTE
    print(
        "Time spent reading data:"
        f" {read_time_in_minutes}m {read_time_in_seconds:.2f}s")

    print("Postprocessing data...")
    reader.postprocess()

    grid = reader.grid
    frame_to_new_timestamp = reader.frame_to_new_timestamp
    num_frames_in_animation = grid.response.shape[0]  # equal to n timesteps

    blue_marble_img = reader.blue_marble_img

    # set up plotting configuration
    # TODO: can provide the timesteps array here if you want!!
    # subclass this config and specialize it...
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
    # TODO: ugly hack to modify config inplace
    config.frame_to_new_timestamp = frame_to_new_timestamp
    config.timestamp_x_pos = timestamp_x_pos
    config.timestamp_y_pos = timestamp_y_pos

    config.show_colorbar = show_colorbar
    config.netcdf_response_var_short_name = netcdf_response_var_short_name
    config.netcdf_response_var_units = reader.mfdataset[
        netcdf_response_var_short_name].attrs.get("units")

    config.mask_threshold_abs_value = mask_threshold_abs_value

    # write the frames to disk
    animator = ICONModelAnimator(
        grid=grid, config=config, blue_marble_img=blue_marble_img)

    print("Making animation...")
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
        help="Flag to save animation as gif from generated frames. (required).",
        required=True)

    read_group = parser.add_argument_group("read")

    read_group.add_argument(
        "--netcdf-response-var-file-path",
        nargs="+",
        type=str,
        help="path or paths or file glob to netcdf input data. (required)",
        required=True)

    default_netcdf_response_var_short_name: str = "u"
    read_group.add_argument(
        "--netcdf-response-var-short-name",
        help="short name of variable to plot over time"
        f" (default: {default_netcdf_response_var_short_name})",
        type=str,
        default=default_netcdf_response_var_short_name)

    read_group.add_argument(
        "--concat-dim", type=str, default=None,
        help="name of axis to manually concatenate on for xarray."
        " (e.g., 'time' would mean that for poorly labeled NetCDF"
        " files for which the time coordinate does not correspond"
        " to the actual output interval, the concatenation over the"
        " time axis will still occur correctly)")

    default_level_ix = 72  # based on conversation with P. Ghosh
    read_group.add_argument(
        "--level-ix",
        type=int,
        help="the level at which to plot the ICON data."
        f" (default: {default_level_ix})",
        default=default_level_ix
    )

    try:
        default_blue_marble_path = Path(
            "assets/world.topo.bathy.200412.3x5400x2700.jpg")
        blue_marble_required = False
    except KeyError:
        default_blue_marble_path = None
        blue_marble_required = True
    read_group.add_argument(
        "--blue-marble-path",
        type=str,
        help=f"path to blue marble PNG. (default: {default_blue_marble_path})",
        default=default_blue_marble_path,
        required=blue_marble_required)

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

    config_group.add_argument(
        "--show-timestamp",
        help=(
            "Flag to show each frame with a timestamp from the data"
            " (default: False)"),
        action=BooleanOptionalAction,
        default=False, )

    # TODO: could add position information for where the timestamp could go
    # e.g., x-y coordinates of this ...

    config_group.add_argument(
        "--time-delta-in-hours-between-consecutive-files",
        type=int,
        help="difference in hours between outputs in consecutive files."
        " E.g., 6 implies 6 hour difference between consecutive files"
        " (default: None).",
        default=None)

    default_timestamp_x_pos = 0.942
    config_group.add_argument(
        "--timestamp-x-pos",
        type=float,
        help="relative x-position of timestamp."
        f" (default: {default_timestamp_x_pos})",
        default=default_timestamp_x_pos
    )

    default_timestamp_y_pos = 0.975
    config_group.add_argument(
        "--timestamp-y-pos",
        type=float,
        help="relative y-position of timestamp."
        f" (default: {default_timestamp_y_pos})",
        default=default_timestamp_y_pos
    )

    config_group.add_argument(
        "--show-colorbar",
        help=(
            "Flag to show colorbar for the data (default: False)"),
        action=BooleanOptionalAction,
        default=False,)

    # TODO: could add a mask greater than threshold as well...
    config_group.add_argument(
        "--mask-threshold-abs-value",
        help="response data above and below this value is not plotted."
        " (default: None)",
        type=float,
        default=None)

    args = parser.parse_args()

    if (args.show_timestamp
            and args.time_delta_in_hours_between_consecutive_files is None):
        raise ValueError

    assert args.timestamp_x_pos >= 0 and args.timestamp_x_pos <= 1.0
    assert args.timestamp_y_pos >= 0 and args.timestamp_y_pos <= 1.0
    return args


class ICONMultifileDataReader(AbstractReader):
    """Read and postprocess multifile ICON data (e.g., gravity wave)."""

    def __init__(
        self,
        netcdf_response_var_file_path: str,
        netcdf_response_var_short_name: str,
        blue_marble_path: str,
        concat_dim: str = None,

        show_timestamp: bool = False,
        time_delta_in_hours_between_consecutive_files: int = 6,

        level_ix: int = 0,
        level_name: str = "lev",
        min_vertical_layer_height_in_meters: float = (
            ICONConfigConsts.TROPOSPHERE_BEGIN_HEIGHT_IN_METERS),
        max_vertical_layer_height_in_meters: float = (
            ICONConfigConsts.TROPOSPHERE_END_HEIGHT_IN_METERS)):

        # TODO: keep public for now
        self.netcdf_response_var_file_path = netcdf_response_var_file_path
        self.netcdf_response_var_short_name = (
            netcdf_response_var_short_name)
        self.blue_marble_path = blue_marble_path

        self.concat_dim = concat_dim

        self.time_delta_in_hours_between_consecutive_files = (
            time_delta_in_hours_between_consecutive_files)

        # TODO: put in config class?
        self.level_name = level_name

        self.level_ix = level_ix

        # Initialize read variables
        self.mfdataset = None
        self.response = None
        self.latitude = None
        self.longitude = None

        # initialize post process vars
        self.frame_to_new_timestamp = None
        self.show_timestamp = show_timestamp
        self.time_delta_in_hours_between_consecutive_files = (
            time_delta_in_hours_between_consecutive_files)

        # TODO: make property?
        self.blue_marble_img = None
        return

    def read(self):
        # load only the response variable to save memory
        data_vars = cdo.showname(
            input=self.netcdf_response_var_file_path[0],
            autoSplit=' ')
        data_vars_to_drop = [
            var for var in data_vars
            if var != self.netcdf_response_var_short_name]

        self.mfdataset = xarr.open_mfdataset(
            self.netcdf_response_var_file_path,
            drop_variables=data_vars_to_drop,
            concat_dim=self.concat_dim,
            combine="nested" if self.concat_dim is not None else "by_coords")

        self.response: xarr.DataArray = (
            self.mfdataset[self.netcdf_response_var_short_name])
        print(self.response)

        self.latitude: ndarray = (
            self.mfdataset
            .variables
            .get(ICONConfigConsts.LATITUDE_NETCDF_SHORT_VAR_NAME)
            .values)

        self.longitude: ndarray = (
            self.mfdataset
            .variables
            .get(ICONConfigConsts.LONGITUDE_NETCDF_SHORT_VAR_NAME)
            .values)

        # for plotting blue marble in animator (note: move elsewhere??)
        self.blue_marble_img = imread(self.blue_marble_path)

        return

    def postprocess(self):
        self.response = self.response.isel({self.level_name: self.level_ix})

        if self.show_timestamp:
            time = self.mfdataset["time"].compute().values
            n_frames = self.response.shape[0]
            t_start = time[0]
            delta = np.timedelta64(
                self.time_delta_in_hours_between_consecutive_files, "h")
            self.frame_to_new_timestamp = self._generate_np_datetimes(
                t_start, n_frames, delta)
        return

    @staticmethod
    def _generate_np_datetimes(
            start: np.datetime64,
            n_steps: int,
            delta: np.timedelta64) -> np.ndarray:
        """
        Generate a sequence of datetimes using NumPy datetime64.

        Parameters
        ----------
        start : np.datetime64
            The initial datetime (t0).
        n_steps : int
            Number of steps to generate (including t0).
        delta : np.timedelta64
            Time difference between consecutive steps.

        Returns
        -------
        np.ndarray
            Array of np.datetime64 values.
        """
        steps = np.arange(n_steps) * delta
        return (start + steps).astype('datetime64[s]')

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

        self._mesh = None
        self.textbox = None
        return

    def _plot_initial_frame(self):
        # Plot an actual image of the Earth
        self._ax.imshow(
            self._blue_marble_img,
            extent=self._config.blue_marble_extent,
            transform=self._config.transform,
            # TODO: could make zorder a part of configure...
            zorder=0,)

        t0 = 0

        # Initialize the timestamp lable
        if self._config.frame_to_new_timestamp is not None:
            self.textbox = self._ax.text(
                self._config.timestamp_x_pos, self._config.timestamp_y_pos,
                self._config.frame_to_new_timestamp[t0],
                ha="center", va="center",
                fontsize=14,
                bbox=dict(facecolor="white", edgecolor="black",
                          boxstyle="round,pad=0.5"),
                transform=self._ax.transAxes,
                zorder=100
            )

        # cache response quantiles before modifying grid response in place
        # TODO: make arguments to script or allow provision of particular
        # vmin/vmax
        response_95th_quantile = self._grid.response.quantile(
            0.95).compute().values
        response_5th_quantile = self._grid.response.quantile(
            0.05).compute().values

        # Keep only grid response values above threshold
        # TODO: this is accessing private variables...
        if self._config.mask_threshold_abs_value is not None:
            print("Masking data...")
            response = self._grid.response
            leq_geq_mask = (
                (response >= abs(self._config.mask_threshold_abs_value)) |
                (response <= -abs(self._config.mask_threshold_abs_value))
            )
            self._grid._response = self._grid.response.where(leq_geq_mask)

        # overlay the data on the blue marble
        response_at_time: ndarray = self._grid.response.isel(
            time=t0).compute().values
        self._mesh = self._ax.pcolormesh(
            self._grid.longitude,
            self._grid.latitude,
            response_at_time,
            # TODO: could make zorder a part of configure...
            zorder=2,  # must have for data plotted "on top of" blue marble
            antialiased=True,
            transform=self._config.transform,
            alpha=self._config.netcdf_var_transparency_on_plot,
            cmap=self._config.netcdf_var_cmap_on_plot)

        # self._mesh.set_clim((response_at_time.min(), response_at_time.max()))
        # TODO: should use global max/min here... but then brighten colors
        # somehow... this is currently dimming the outputs it seems... maybe
        # better to use 95% percentile or something... and what about cmap
        # extend??? in the areas with really high or low velocity, will info
        # be lost??
        # self._mesh.set_clim(min_response, max_response)

        self._mesh.set_clim(response_5th_quantile, response_95th_quantile)

        if self._config.show_colorbar:
            print("Showing colorbar...")

            # describe colorbar location
            cax = inset_axes(
                self._ax,
                width="35%",
                height="2%",
                loc="lower center",
                borderpad=4  # keep colorbar from "falling off" image
            )

            self.colorbar = self._fig.colorbar(
                self._mesh,
                ax=self._ax,
                cax=cax,
                label=f"{self._config.netcdf_response_var_short_name}"
                f" ({self._config.netcdf_response_var_units})",
                orientation="horizontal",
                location="bottom",
                extend="both")

        return

    def _update_frame(self, frame: int):
        if self._config.frame_to_new_timestamp is not None:
            self.textbox.set_text(self._config.frame_to_new_timestamp[frame])

        # Update frame with the value of the response variable at next
        # frame where frame == timestep (e.g., 12 timesteps, 12 frames)
        response_at_time: ndarray = self._grid.response.isel(
            time=frame).compute().values

        self._mesh.set_array(response_at_time)

        return


if __name__ == "__main__":
    main()
