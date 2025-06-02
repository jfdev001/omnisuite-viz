from abc import ABC, abstractmethod
from omnisuite_examples.grid import Grid


class Animator(ABC):
    @abstractmethod
    def __init__(self, grid: Grid):
        pass

    @abstractmethod
    def animate(self):
        pass

    @abstractmethod
    def save_animation(self):
        pass

    @abstractmethod
    def _save_frames(self):
        pass

    @abstractmethod
    def _plot_initial_frame(self):
        pass

    @abstractmethod
    def _update_frame(self):
        pass
