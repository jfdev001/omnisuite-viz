from dataclasses import dataclass
from typing import ClassVar

from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.grid import WorldMapGrid
from omnisuite_examples.animator_config import NetcdfAnimatorConfig


def main():
    args = cli()
    grid = WorldMapGrid()
    config = ICONModelAnimatorConfig(
        save_animation=save_animation,
        output_dir=output_dir)
    animator = ICONModelAnimator(grid=grid, config=config)
    animator.animate()
    pass


def cli():
    pass


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
        # TODO: load height variable
        # TODO: load output variable data
        # TODO: scale/average accordingly
        return


class ICONModelAnimator(OmniSuiteWorldMapAnimator):
    # plot the desired initial frame (see also speedyweather animator)
    # update according to time step and use of output var frame....
    pass


if __name__ == "__main__":
    main()
