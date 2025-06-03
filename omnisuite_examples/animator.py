from abc import ABC, abstractmethod
from cartopy.crs import PlateCarree
import matplotlib.pyplot as plt

from omnisuite_examples.grid import Grid, WorldMapGrid
from omnisuite_examples.animator_config import (AnimatorConfig,
                                                OmniSuiteWorldMapAnimatorConfig)


class Animator(ABC):

    def __init__(self, grid: Grid, config: AnimatorConfig):
        self._grid = grid
        self._config = config
        return

    def animate(self):
        self._plot_initial_frame()
        self._save_frames()
        if self._config.save_animation:
            self._save_frames_as_animation()
        return

    @abstractmethod
    def _save_frames(self):
        pass

    @abstractmethod
    def _save_frames_as_animation(self):
        """Save the frames as some animation (e.g., gif, mp4, etc.)"""
        pass

    @abstractmethod
    def _plot_initial_frame(self):
        pass

    @abstractmethod
    def _update_frame(self):
        pass


class OmniSuiteWorldMapAnimator(Animator):

    def __init__(
            self, grid: WorldMapGrid, config: OmniSuiteWorldMapAnimatorConfig):
        self._grid = grid
        self._config = config
        return

    def _plot_initial_frame(self):
        self._fig = plt.figure(figsize=self._config.figsize)
        self._ax = plt.axes(projection=self.projection)
        self._ax.coastlines()

        return

    def _save_frames(self):

        return

    def _update_frame(self):
        return

    def _save_frames_as_animation(self):
        return
