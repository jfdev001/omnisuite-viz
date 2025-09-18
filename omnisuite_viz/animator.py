"""Classes for writing/animating frames that can be imported into OmniSuite."""
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from os import listdir
from os.path import join, getctime
from PIL import Image
from typing import List
from subprocess import run
from warnings import warn

from tqdm import tqdm

from omnisuite_viz.grid import Grid, LatLonGrid
from omnisuite_viz.animator_config import (
    AnimatorConfig, OmniSuiteAnimatorConfig)


class Animator(ABC):

    def __init__(self, grid: Grid, config: AnimatorConfig, *args, **kwargs):
        self._grid = grid
        self._config = config
        return

    def animate(self):
        self._configure_initial_frame()
        self._plot_initial_frame()
        self._update_and_save_frames()
        if self._config.save_animation:
            self._save_animation()
        print(f"Results written to: {self._config.output_dir}")
        return

    @abstractmethod
    def _configure_initial_frame():
        raise NotImplementedError

    @abstractmethod
    def _plot_initial_frame(self):
        raise NotImplementedError

    @abstractmethod
    def _update_and_save_frames(self):
        raise NotImplementedError

    @abstractmethod
    def _update_frame(self, frame: int):
        raise NotImplementedError

    def _save_animation(self):
        frames = self._open_frames()
        self._save_frames_as_animation(frames)
        self._close_frames(frames)
        return

    @abstractmethod
    def _open_frames(self):
        raise NotImplementedError

    @abstractmethod
    def _save_frames_as_animation(self, frames):
        raise NotImplementedError

    @abstractmethod
    def _close_frames(self, frames):
        raise NotImplementedError


class OmniSuiteWorldMapAnimator(Animator):
    """Animate world map frames that can be used in OmniSuite."""
    @staticmethod
    def get_rectangle_for_full_plot_on_omniglobe():
        rectangle_for_full_plot_on_omniglobe = [0, 0, 1, 1]
        return rectangle_for_full_plot_on_omniglobe

    def __init__(self, grid: LatLonGrid, config: OmniSuiteAnimatorConfig):
        self._grid = grid
        self._config = config
        return

    def _configure_initial_frame(self):
        self._fig = plt.figure(figsize=self._config.figsize)
        self._ax = plt.axes(
            self.get_rectangle_for_full_plot_on_omniglobe(),
            projection=self._config.projection)
        self._ax.axis("off")
        self._ax.coastlines(**self._config.coastlines_kwargs)
        return

    def _plot_initial_frame(self):
        return

    def _update_and_save_frames(self):
        for frame in tqdm(
                range(self._config.num_frames_in_animation),
                desc="Updating frames"):
            self._update_frame(frame)
            frame_path = join(
                self._config.output_dir,
                self._config.formatted_file_name_per_frame % frame)
            self._fig.savefig(frame_path)
        return

    def _update_frame(self, frame: int):
        self._ax.text(0, frame, frame)  # arbitrary modification needed for gif
        return

    def _open_frames(self) -> List[Image.Image]:
        files_sorted_by_creation_date = sorted(
            listdir(self._config.output_dir),
            key=lambda fpath: getctime(join(self._config.output_dir, fpath)))
        frames: List[Image.Image] = [
            Image.open(join(self._config.output_dir, f))
            for f in files_sorted_by_creation_date]
        return frames

    def _save_frames_as_animation(self, frames: List[Image.Image]):
        has_ffmpeg = run(
            ["which", "ffmpeg"], capture_output=True).returncode == 0
        if has_ffmpeg:
            output_palettegen = run(
                [
                    "ffmpeg",
                    "-loglevel",
                    "fatal",
                    "-i",
                    # TODO: should use frame naming convention here instead...
                    f"{self._config.output_dir}/frame_%d.png",
                    "-vf",
                    "palettegen",
                    f"{self._config.output_dir}/palette.png"
                ]
            )
            if output_palettegen.returncode != 0:
                print(output_palettegen)
                raise
            output_gif_gen = run(
                [
                    "ffmpeg",
                    "-framerate",
                    "2",  # TODO: make configurable? not worth effot...
                    "-loglevel",
                    "fatal",
                    "-i",
                    f"{self._config.output_dir}/frame_%d.png",
                    "-i",
                    f"{self._config.output_dir}/palette.png",
                    "-filter_complex",
                    "paletteuse",
                    f"{self._config.path_to_save_animation}"
                ]
            )
            if output_gif_gen.returncode != 0:
                print(output_gif_gen)
                raise
        else:
            msg = (
                "Using PIL by default to create animation may lead to"
                " artifacts in the animation. Refer to the README.md"
                " on installing `ffmpeg` as this is the preferred tool"
                " for creating animations, or just go to"
                "https://johnvansickle.com/ffmpeg/"
            )
            warn(message=msg)
            frames[0].save(
                self._config.path_to_save_animation,
                save_all=True,
                append_images=frames[1:],
                loop=self._config.pil_image_gif_loop,
                duration=self._config.pil_image_duration_between_frames_in_ms)
        return

    def _close_frames(self, frames: List[Image.Image]):
        for frame in frames:
            frame.close()
        return
