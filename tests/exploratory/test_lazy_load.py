from unittest import TestCase, main
import xarray as xarr
import netCDF4
from pdb import set_trace


class TestLazyLoad(TestCase):
    def test_lazy_load(self):
        gravity_wave_december_paths = "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212*"

        # TODO: could more intelligently select chunks and time dim
        print("loading data...")
        concat_data = xarr.open_mfdataset(
            gravity_wave_december_paths, chunks=13, concat_dim="time", 
            combine="nested")
        regular_data = xarr.open_mfdataset(
            gravity_wave_december_paths, chunks=13)

        print(concat_data)
        print(regular_data)

        return


if __name__ == "__main__":
    main()
