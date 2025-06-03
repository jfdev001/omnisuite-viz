from cartopy.crs import Projection, PlateCarree
from dataclasses import dataclass
from matplotlib.pyplot import rcParams
from os.path import exists
from typing import ClassVar, Tuple


@dataclass
class AnimatorConfig:
    INCH_PER_PIXEL: ClassVar[float] = 1 / rcParams['figure.dpi']
    save_animation: bool
    output_dir: str

    def __post_init__(self):
        assert exists(self.output_dir)


@dataclass
class OmniSuiteAnimatorConfig(AnimatorConfig):
    global_width_in_pixels: int = 4096
    global_height_in_pixels: int = 2048
    figsize: Tuple[int, int] = (
        global_width_in_pixels*AnimatorConfig.INCH_PER_PIXEL,
        global_width_in_pixels*AnimatorConfig.INCH_PER_PIXEL)


@dataclass
class WorldMapAnimatorConfig(AnimatorConfig):
    projection: Projection = PlateCarree()


@dataclass
class OmniSuiteWorldMapAnimatorConfig(
        OmniSuiteAnimatorConfig, WorldMapAnimatorConfig):
    pass
