from __future__ import annotations

from dataclasses import dataclass
from matplotlib.pytplot import imread
from netCDF4 import Dataset
from typing import ClassVar

from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.grid import WorldMapNetcdfGrid
from omnisuite_examples.animator_config import NetcdfAnimatorConfig


def main():
    # cli
    args = cli()
    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels
    save_animation: bool = args.save_animation
    output_dir: str = args.output_dir
    netcdf_response_var_file_path: str = args.netcdf_response_var_file_path
    netcdf_long_name_of_response_var: str =\
        args.netcdf_long_name_of_response_var
    blue_marble_path: str = args.blue_marble_path

    config = ICONModelAnimatorConfig(
        plot_height_in_pixels=plot_height_in_pixels,
        plot_width_in_pixels=plot_width_in_pixels,
        blue_marble_path=blue_marble_path,
        netcdf_response_var_file_path=netcdf_response_var_file_path,
        netcdf_long_name_of_response_var=netcdf_long_name_of_response_var,
        save_animation=save_animation,
        output_dir=output_dir)

    grid = ICONModelGrid(latitude=config.latitude, longitude=config.longitude)

    animator = ICONModelAnimator(grid=grid, config=config)
    animator.animate()

    return


def cli():
    pass


class ICONModelGrid(WorldMapNetcdfGrid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return


@dataclass(kw_only=True)
class ICONModelAnimatorConfig(NetcdfAnimatorConfig):
    TROPOSPHERE_BEGIN_HEIGHT_IN_METERS: ClassVar[float] = 0
    TROPOSPHERE_END_HEIGHT_IN_METERS: ClassVar[float] = 10_000

    netcdf_height_file_path: str
    netcdf_long_name_of_height_var_to_determine_vertical_layer: str = \
        "geometric height at full level center"
    min_height_in_meters_for_vertical_layer: float =\
        TROPOSPHERE_END_HEIGHT_IN_METERS
    max_height_in_meters_for_vertical_layer: float =\
        TROPOSPHERE_END_HEIGHT_IN_METERS

    def __post_init__(self):
        super().__post_init__()

        # TODO: this is side effect heavy and not ideal for testing...
        netcdf_response_var_file = Dataset(
            self.netcdf_response_var_file_path)
        netcdf_height_file = Dataset(self.netcdf_height_file_path)

        response_variables = netcdf_response_var_file.variables
        height_variables = netcdf_height_file.variables

        self.latitude = response_variables[self.LATITUDE_NETCDF_VAR_NAME]
        self.longitude = response_variables[self.LONGITUDE_NETCDF_VAR_NAME]

        netcdf_long_name_to_netcdf_var_name = {
            self.ncfile.variables[var].long_name: var
            for var in self.ncfile.variables.keys()}

        # load height variable
        netcdf_height_var_name = netcdf_long_name_to_netcdf_var_name[
            self.netcdf_long_name_of_height_var_to_determine_vertical_layer]
        self.height_in_meters = height_variables[netcdf_height_var_name]

        # load output variable data
        netcdf_response_var_name = netcdf_long_name_to_netcdf_var_name[
            self.netcdf_long_name_of_response_var]
        self.response_var = response_variables[netcdf_response_var_name]

        # TODO: scale/average accordingly
        pass

        # TODO: load blue marble... should probably do this in animator?
        self.blue_marble_img = imread(self.blue_marble_path)
        return

    def __del__(self):
        self.netcdf_response_var_file.close()
        self.netcdf_height_file.close()
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
