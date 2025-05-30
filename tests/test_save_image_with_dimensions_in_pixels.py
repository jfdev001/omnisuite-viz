import unittest
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import tempfile
import os


class TestSaveImageWithDimensionsInPixels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        px = 1/plt.rcParams['figure.dpi']
        cls.mpl_width_in_pixels = 4096
        cls.mpl_height_in_pixels = 2048
        cls.figsize = (cls.mpl_width_in_pixels*px,
                       cls.mpl_height_in_pixels*px)
        return

    def test_matplotlib_example(self):
        """Verify https://matplotlib.org/stable/gallery/subplots_axes_and_figures/figure_size_units.html#figure-size-in-pixel"""
        fig, ax = plt.subplots(figsize=self.figsize)
        self.assert_tempfile_mpl_image_dimensions_match_saved_image_dimensions(
            fig)
        plt.close()

        return

    def test_cartopy_single_frame_example(self):
        fig = plt.figure(figsize=self.figsize)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        self.assert_tempfile_mpl_image_dimensions_match_saved_image_dimensions(
            fig)
        plt.close()
        return

    def test_cartopy_multi_frame_from_mpl_animation_example(self):
        fig = plt.figure(figsize=self.figsize)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        mesh = ax.pcolormesh(np.random.randn(10, 10))

        def update_animation_clojure(fig, temp_dir_name, mesh):
            def update(f):
                mesh.set_array(np.random.randn(10, 10).ravel())
                fig.savefig(os.path.join(temp_dir_name, f"{f}.png"))
                return [mesh]
            return update

        with tempfile.TemporaryDirectory() as temp_dir_name:
            animation = FuncAnimation(
                fig,
                update_animation_clojure(fig, temp_dir_name, mesh),
                frames=2)

            animation.save(os.path.join(temp_dir_name, "anim.gif"))

            for f in os.listdir(temp_dir_name):
                if ".png" in f:
                    fpath_of_animation_frame = os.path.join(temp_dir_name, f)
                    self.assert_image_dimensions(fpath_of_animation_frame)

        return

    def assert_tempfile_mpl_image_dimensions_match_saved_image_dimensions(self, fig):
        with tempfile.NamedTemporaryFile(suffix=".png") as tfp:
            temp_fpath = tfp.name
            fig.savefig(temp_fpath)
            tfp.flush()
            self.assert_image_dimensions(temp_fpath)
        return

    def assert_image_dimensions(self, temp_fpath):
        print(temp_fpath)
        with Image.open(temp_fpath) as image:
            image_width_in_pixels = image.width
            image_height_in_pixels = image.height
            print(image_width_in_pixels, image_height_in_pixels)
            self.assertEqual(image_width_in_pixels,
                             self.mpl_width_in_pixels)
            self.assertEqual(image_height_in_pixels,
                             self.mpl_height_in_pixels)


if __name__ == "__main__":
    unittest.main()
