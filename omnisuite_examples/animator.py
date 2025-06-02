from abc import ABC, abstractmethod
from cartopy.crs import PlateCarree
import matplotlib.pyplot as plt
from os.path import exists

from omnisuite_examples.grid import Grid, WorldMapGrid


class Animator(ABC):
    INCH_PER_PIXEL = 1/plt.rcParams['figure.dpi']

    @abstractmethod
    def __init__(self, grid: Grid, output_dir: str):
        pass

    @property
    def output_dir(self) -> str:
        assert exists(self._output_dir)
        return self._output_dir

    def animate(self, save_animation: bool):
        self._plot_initial_frame()
        self._save_frames()
        if save_animation:
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


class WorldMapAnimator(Animator):
    # TODO: what if you want multiple instances of WorldMapAnimator... each
    # with different configuration here...
    # TODO: This config stuff is not related to the test!!!
    projection = PlateCarree()

    # add an nframes term needed for update frames???
    # figsize = (4096*Animator.INCH_PER_PIXEL, 2048*Animator.INCH_PER_PIXEL)

    def __init__(self, grid: WorldMapGrid, output_dir: str):
        self._grid = grid

        self._output_dir = output_dir

        self._fig = None
        self._ax = None
        return

    def _plot_initial_frame(self):
        self._fig = plt.figure()
        self._ax = plt.axes(projection=self.projection)
        self._ax.coastlines()
        return

    def _save_frames(self):

        return

    def _update_frame(self):
        return

    def _save_frames_as_animation(self):
        return
