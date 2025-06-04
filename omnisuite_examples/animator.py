from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from noise import pnoise3
from numpy import zeros_like
from os import listdir
from os.path import join
import pdb
from PIL import Image
from typing import List
from tqdm import tqdm

from omnisuite_examples.grid import Grid, WorldMapGrid
from omnisuite_examples.animator_config import (
    AnimatorConfig, OmniSuiteAnimatorConfig)


class Animator(ABC):

    def __init__(self, grid: Grid, config: AnimatorConfig):
        self._grid = grid
        self._config = config
        return

    def animate(self):
        self._plot_initial_frame()
        self._update_and_save_frames()
        if self._config.save_animation:
            self._save_animation()
        print(f"Results written to: {self._config.output_dir}")
        return

    @abstractmethod
    def _plot_initial_frame(self):
        pass

    @abstractmethod
    def _update_and_save_frames(self):
        pass

    @abstractmethod
    def _update_frame(self, frame: int):
        pass

    def _save_animation(self):
        frames = self._open_frames()
        self._save_frames_as_animation(frames)
        self._close_frames(frames)
        return

    @abstractmethod
    def _open_frames(self):
        pass

    @abstractmethod
    def _save_frames_as_animation(self, frames):
        pass

    @abstractmethod
    def _close_frames(self, frames):
        pass


class OmniSuiteWorldMapAnimator(Animator):

    def __init__(
            self, grid: WorldMapGrid, config: OmniSuiteAnimatorConfig):
        self._grid = grid
        self._config = config
        self._fig = None
        self._ax = None
        return

    def _plot_initial_frame(self):
        self._fig = plt.figure(figsize=self._config.figsize)
        self._ax = plt.axes(projection=self._config.projection)
        self._ax.coastlines()

        return

    def _load_base_map(self):
        img = plt.imread(self._config.base_map_path)
        img_extent = (-180, 180, -90, 90)  # TODO: config for local area
        img_proj = self._config.projection  # TODO: make config? prob not
        return img, img_extent, img_proj

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
        self._ax.text(0, frame, frame)  # arbitrary modification
        return

    def _open_frames(self) -> List[Image.Image]:
        frames: List[Image.Image] = [
            Image.open(join(self._config.output_dir, f))
            for f in listdir(self._config.output_dir)]
        return frames

    def _save_frames_as_animation(self, frames: List[Image.Image]):
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


class PerlinNoiseAnimator(OmniSuiteWorldMapAnimator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._latitude_mesh = self._grid.latitude_mesh
        self._longitude_mesh = self._grid.longitude_mesh
        self._perlin_noise_field = zeros_like(self._latitude_mesh)

        # NOTE: could create a new Config class with perlin noise values
        self._spatial_scale = 0.05
        self._temporal_scale = 0.02
        self._seed = 42
        return

    def _plot_initial_frame(self):
        """

        References:
        [1]: https://gradsaddict.blogspot.com/2019/12/python-tutorial-blue-and-black-marble.html
        """
        self._fig = plt.figure(figsize=self._config.figsize)
        self._ax = plt.axes(projection=self._config.projection)
        # TODO: it seems the coastlines must be reducing the extent or something
        # here since the natural earth PNG in the in material editor loads
        # appropriately...
        self._ax.coastlines(linewidth=5, color="red")
        base_map_image, base_map_extent, base_map_projection =\
            self._load_base_map()
        self._ax.imshow(
            base_map_image,
            extent=base_map_extent,
            transform=base_map_projection,
            origin='upper')

        # if you don't initialize the noise field, pcolormesh renders nothing
        # pdb.set_trace()
        # self._update_perlin_noise_field(0)

        # TODO: does pmesh correspond correctly to expected extent???
        # self._mesh = self._ax.pcolormesh(
        # self._grid.longitude,
        # self._grid.latitude,
        # self._perlin_noise_field,
        # transform=self._config.projection,
        # cmap="coolwarm"
        # )

        return

    def _update_frame(self, frame: int):
        # self._update_perlin_noise_field(frame)
        # self._mesh.set_array(self._perlin_noise_field.ravel())
        return

    def _update_perlin_noise_field(self, frame: int):
        for i in range(self._perlin_noise_field.shape[0]):
            for j in range(self._perlin_noise_field.shape[1]):
                self._perlin_noise_field[i, j] = pnoise3(
                    self._spatial_scale * self._longitude_mesh[i, j],
                    self._spatial_scale * self._latitude_mesh[i, j],
                    frame * self._temporal_scale,
                    repeatx=360,
                    repeaty=180,
                    base=self._seed)
        return
