from unittest import TestCase, main
import xarray as xarr
import numpy as np
import netCDF4
from pdb import set_trace
from datetime import datetime, timedelta
from typing import List


import numpy as np

def generate_np_datetimes(start: np.datetime64, n_steps: int, delta: np.timedelta64) -> np.ndarray:
    """
    Generate a sequence of datetimes using NumPy datetime64.

    Parameters
    ----------
    start : np.datetime64
        The initial datetime (t0).
    n_steps : int
        Number of steps to generate (including t0).
    delta : np.timedelta64
        Time difference between consecutive steps.

    Returns
    -------
    np.ndarray
        Array of np.datetime64 values.
    """
    steps = np.arange(n_steps) * delta
    return (start + steps).astype('datetime64[s]')


class TestTimestamps(TestCase):
    def test_timestamps(self):
        gravity_wave_december_paths = "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212*"

        print("loading data...")
        concat_data = xarr.open_mfdataset(
            gravity_wave_december_paths, concat_dim="time", 
            combine="nested")
        print(concat_data)

        time = concat_data["time"].compute().values
        delta = np.timedelta64(6, "h")
        newtimes = generate_np_datetimes(time[0], len(time), delta)
        set_trace()
        return


if __name__ == "__main__":
    main()
