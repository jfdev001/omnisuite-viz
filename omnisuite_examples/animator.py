from abc import ABC, abstractmethod
from omnisuite_examples.grid import Grid, WorldMapGrid
from os.path import exists


class Animator(ABC):
    @abstractmethod
    def __init__(self, grid: Grid, output_dir: str):
        pass

    @property
    def output_dir(self) -> str:
        assert exists(self._output_dir)
        return self._output_dir

    @abstractmethod
    def animate(self, save_animation: bool):
        pass

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
    def __init__(self, grid: WorldMapGrid, output_dir: str):
        self._grid = grid
        self._output_dir = output_dir
        return

    def animate(self, save_animation: bool):
        self._plot_initial_frame()
        self._save_frames()
        if save_animation:
            self._save_frames_as_animation()
        return

    def _save_frames(self):
        return

    def _save_frames_as_animation(self):
        return

    def _plot_initial_frame(self):
        return

    def _update_frame(self):
        return
