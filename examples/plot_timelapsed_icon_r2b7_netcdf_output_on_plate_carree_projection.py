
from omnisuite_examples.animator import OmniSuiteWorldMapAnimator
from omnisuite_examples.grid import WorldMapGrid
from omnisuite_examples.animator_config import OmniSuiteAnimatorConfig


def main():
    args = cli()
    grid = WorldMapGrid()
    config = ICONModelAnimatorConfig()
    animator = ICONModelAnimator(grid=grid, config=config)
    animator.animate()
    pass


def cli():
    pass


class ICONModelAnimatorConfig(OmniSuiteAnimatorConfig):
    pass


class ICONModelAnimator(OmniSuiteWorldMapAnimator):
    pass


if __name__ == "__main__":
    main()
