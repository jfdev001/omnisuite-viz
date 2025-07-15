from os import listdir
from PIL import Image
import unittest

from tests.animator_test_mixin import AnimatorTestMixin
from omnisuite_viz.grid import WorldMapRectangularGrid
from omnisuite_viz.animator import OmniSuiteWorldMapAnimator
from omnisuite_viz.animator_config import OmniSuiteAnimatorConfig


class TestOmniSuiteWorldMapAnimator(AnimatorTestMixin, unittest.TestCase):
    def make_concrete_animator(self):

        grid = WorldMapRectangularGrid()

        self.output_dir = self.temp_dir.name
        self.num_frames_in_animation = 2
        self._config = OmniSuiteAnimatorConfig(
            save_animation=False,
            output_dir=self.output_dir,
            num_frames_in_animation=self.num_frames_in_animation)

        omnisuite_world_map_animator = OmniSuiteWorldMapAnimator(
            grid, self._config)

        return omnisuite_world_map_animator

    def assert_animate(self):
        self.assertEqual(
            len(listdir(self.output_dir)), self.num_frames_in_animation)
        return


if __name__ == "__main__":
    unittest.main()
