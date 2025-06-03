import pdb
from PIL import Image
import tempfile
import unittest

from tests.animator_test_mixin import AnimatorTestMixin
from omnisuite_examples.grid import WorldMapGrid
from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.animator_config import OmniSuiteAnimatorConfig


class TestOmniSuiteWorldMapAnimator(AnimatorTestMixin, unittest.TestCase):
    def make_concrete_animator(self):

        grid = WorldMapGrid()

        output_dir = self.temp_dir.name
        self.num_frames_in_animation = 5
        self._config = OmniSuiteAnimatorConfig(
            save_animation=True,
            output_dir=output_dir,
            num_frames_in_animation=self.num_frames_in_animation)

        omnisuite_world_map_animator = OmniSuiteWorldMapAnimator(
            grid, self._config)

        return omnisuite_world_map_animator

    def assert_animate(self):
        """

        An animation was successful when the number of frames in saved
        animation (e.g., gif) matches the expected amount of frames.
        """
        with Image.open(self._config.path_to_save_animation) as gif:
            n_frames_in_gif = gif.n_frames
            self.assertEqual(n_frames_in_gif, self.num_frames_in_animation)
        return


if __name__ == "__main__":
    unittest.main()
