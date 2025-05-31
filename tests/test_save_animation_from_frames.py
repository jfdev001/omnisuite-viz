import matplotlib.pyplot as plt
import os
from PIL import Image
import tempfile
import unittest


class TestSaveAnimationFromFrames(unittest.TestCase):
    def test_save_generic_plots_to_gif(self):
        """

        References:
        [1] :  https://stackoverflow.com/questions/34975972/how-can-i-make-a-video-from-array-of-images-in-matplotlib
        #issuecomment-2917040094
        [2] : https://github.com/SpeedyWeather/SpeedyWeather.jl/issues/737
        """
        fig = plt.figure(figsize=(8, 5))
        plt.plot(range(10), range(10))
        n_expected_frames = 10
        with tempfile.TemporaryDirectory(delete=True) as temp_dir_name:
            for frame in range(n_expected_frames):
                plt.text(0, 0+(1/2)*frame, str(frame))
                fpath = os.path.join(temp_dir_name, f"{frame}.png")
                fig.savefig(fpath)

            # open images, save as gif, then verify number of frames
            frames = [Image.open(f"{temp_dir_name}/{f}.png")
                      for f in range(n_expected_frames)]

            gif_path = f"{temp_dir_name}/pil.gif"
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=500,
                loop=0)

            with Image.open(gif_path) as gif:
                n_frames_in_gif = gif.n_frames
                self.assertEqual(n_frames_in_gif, n_expected_frames)

        return


if __name__ == "__main__":
    unittest.main()
