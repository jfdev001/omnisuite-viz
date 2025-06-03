from cartopy.crs import Projection, PlateCarree
from dataclasses import dataclass
from matplotlib.pyplot import rcParams
from os.path import exists, join
from typing import ClassVar, Tuple, Dict


@dataclass
class AnimatorConfig:

    save_animation: bool
    num_frames_in_animation: int

    output_dir: str
    path_to_save_animation: str = None

    INCH_PER_PIXEL: ClassVar[float] = 1 / rcParams['figure.dpi']
    formatted_file_name_per_frame: str = "%d.png"

    def __post_init__(self):
        assert exists(self.output_dir)

        if self.path_to_save_animation is None:
            self.path_to_save_animation = join(
                self.output_dir, "animation.gif")

        assert self._is_valid_file_name_format()

    def _is_valid_file_name_format(self) -> bool:
        return self._is_valid_percent_format()\
            and self._is_valid_brace_format()

    def _is_valid_brace_format(self) -> bool:
        try:
            self.formatted_file_name_per_frame.format(1)
            return True
        except (IndexError, KeyError, ValueError):
            return False

    def _is_valid_percent_format(self) -> bool:
        try:
            self.formatted_file_name_per_frame % 1
            return True
        except (TypeError, ValueError):
            return False


@dataclass
class OmniSuiteAnimatorConfig(AnimatorConfig):
    plot_width_in_pixels: int = 4096
    plot_height_in_pixels: int = 2048
    figsize: Tuple[int, int] = (
        plot_width_in_pixels*AnimatorConfig.INCH_PER_PIXEL,
        plot_height_in_pixels*AnimatorConfig.INCH_PER_PIXEL)

    pil_image_gif_loop: int = 0
    pil_image_duration_between_frames_in_ms: float = 500

    projection: Projection = PlateCarree()
