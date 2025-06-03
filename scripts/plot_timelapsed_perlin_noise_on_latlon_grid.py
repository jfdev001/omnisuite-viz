from omnisuite_examples.animator import PerlinNoiseAnimator
from omnisuite_examples.animator_config import OmniSuiteAnimatorConfig
from omnisuite_examples.grid import WorldMapGrid
import os
from argparse import ArgumentParser, BooleanOptionalAction

DESCRIPTION = """
Save animation frames (and optionally combine the frames to a gif) of Perlin
noise on Plate-Carree projection.
"""


def main():
    # save and annotate cli args
    args = cli()

    plot_width_in_pixels: int = args.plot_width_in_pixels
    plot_height_in_pixels: int = args.plot_height_in_pixels

    output_dir: str = args.output_dir
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    save_animation: bool = args.save_animation
    num_frames_in_animation: int = args.num_frames_in_animation

    # perform animation
    grid = WorldMapGrid()

    config = OmniSuiteAnimatorConfig(  # TODO: could read from yml/json
        save_animation=save_animation,
        num_frames_in_animation=num_frames_in_animation,
        plot_width_in_pixels=plot_width_in_pixels,
        plot_height_in_pixels=plot_height_in_pixels,
        output_dir=output_dir)

    animator = PerlinNoiseAnimator(grid, config)

    animator.animate()

    return


def cli():
    parser = ArgumentParser(description=DESCRIPTION)

    parser.add_argument("output_dir", type=str,
                        help="destination directory of saved plots")

    parser.add_argument(
        "--save-animation", action=BooleanOptionalAction, default=False)

    default_plot_width_in_pixels = 4096
    parser.add_argument(
        "--plot_width_in_pixels",
        type=int,
        help=f" (default: {default_plot_width_in_pixels})",
        default=default_plot_width_in_pixels)

    default_plot_height_in_pixels = 2048
    parser.add_argument(
        "--plot_height_in_pixels",
        type=int,
        help=f" (default: {default_plot_height_in_pixels})",
        default=default_plot_height_in_pixels)

    default_num_frames_in_animation = 366
    parser.add_argument(
        "--num_frames_in_animation",
        help=f"default: {default_num_frames_in_animation}",
        type=int,
        default=default_num_frames_in_animation)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
