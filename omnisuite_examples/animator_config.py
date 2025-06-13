from cartopy.crs import Projection, PlateCarree
from dataclasses import dataclass, field
from matplotlib.pyplot import rcParams, imread
from os.path import exists, join
from typing import ClassVar, Tuple, Optional
import re


@dataclass(kw_only=True)
class AnimatorConfig:

    save_animation: bool

    output_dir: str
    path_to_save_animation: str = None

    num_frames_in_animation: Optional[int] = None

    INCH_PER_PIXEL: ClassVar[float] = 1 / rcParams['figure.dpi']
    formatted_file_name_per_frame: str = "frame_%d.png"

    def __post_init__(self):
        assert exists(self.output_dir)

        if self.path_to_save_animation is None:
            self.path_to_save_animation = join(
                self.output_dir, "animation.gif")

        # See pg. 41 of OmniSuite 6.0 manual
        # https://globoccess.com/omnisuite/documents/OmniSuite_6-0_manual.pdf
        # makes sure fname matches '[texture-name]_.*'
        valid_omnisuite_animation_file_name_pattern = r"^[a-zA-Z]+_.*$"
        assert re.match(
            valid_omnisuite_animation_file_name_pattern,
            self.formatted_file_name_per_frame)

        assert self._is_valid_percent_format()

    def _is_valid_percent_format(self) -> bool:
        try:
            self.formatted_file_name_per_frame % 1
            return True
        except (TypeError, ValueError):
            return False


@dataclass(kw_only=True)
class OmniSuiteAnimatorConfig(AnimatorConfig):
    plot_width_in_pixels: int = 4096
    plot_height_in_pixels: int = 2048
    figsize: Optional[Tuple[int, int]] = None
    pil_image_gif_loop: int = 0
    pil_image_duration_between_frames_in_ms: float = 500

    projection: Projection = PlateCarree()
    transform: Projection = PlateCarree()

    coastlines_kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if self.figsize is None:
            self.figsize = (
                self.plot_width_in_pixels*AnimatorConfig.INCH_PER_PIXEL,
                self.plot_height_in_pixels*AnimatorConfig.INCH_PER_PIXEL)


@dataclass(kw_only=True)
class NetcdfAnimatorConfig(OmniSuiteAnimatorConfig):
    netcdf_file_path: str

    blue_marble_path: str
    blue_marble_extent = (-180, 180, -90, 90)  # full blue marble

    netcdf_long_name_of_var_to_plot: str

    netcdf_var_transparency_on_plot: float = 0.30
    netcdf_var_cmap_on_plot: str = "bwr"

    def __post_init__(self):
        super().__post_init__()
        assert exists(self.netcdf_file_path), \
            "You can download an example NetCDF file from" +\
            " https://zenodo.org/records/15639060"
        assert exists(self.blue_marble_path), \
            "You can download blue marble PNGs from" +\
            "https://neo.gsfc.nasa.gov/view.php?datasetId=BlueMarbleNG"
        return
