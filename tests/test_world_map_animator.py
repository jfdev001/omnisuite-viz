import unittest
import tempfile

from tests.animator_test_mixin import AnimatorTestMixin
from omnisuite_examples.grid import WorldMapGrid
from omnisuite_examples.animator import WorldMapAnimator


class TestWorldMapAnimator(AnimatorTestMixin, unittest.TestCase):
    def make_concrete_animator(self):
        output_dir = ""  # TODO: use tempfile... elegant way to have context...
        grid = WorldMapGrid()
        world_map_animator = WorldMapAnimator(grid, output_dir)
        return world_map_animator

    def assert_animate(self):
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
