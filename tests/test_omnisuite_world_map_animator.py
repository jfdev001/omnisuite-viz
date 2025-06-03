import unittest
import tempfile

from tests.animator_test_mixin import AnimatorTestMixin
from omnisuite_examples.grid import WorldMapGrid
from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.animator_config import OmniSuiteWorldMapAnimatorConfig


class TestOmniSuiteWorldMapAnimator(AnimatorTestMixin, unittest.TestCase):
    def make_concrete_animator(self):
        output_dir = ""  # TODO: use tempfile... elegant way to have context...
        grid = WorldMapGrid()
        config = OmniSuiteWorldMapAnimatorConfig()
        omnisuite_world_map_animator = OmniSuiteWorldMapAnimator(grid, config)
        return omnisuite_world_map_animator

    def assert_animate(self):
        """

        An animation was successful when the number of frames in saved
        animation (e.g., gif) matches the expected amount of frames.
        """
        raise NotImplementedError

    def cleanup_animate(self):
        pass


if __name__ == "__main__":
    unittest.main()
