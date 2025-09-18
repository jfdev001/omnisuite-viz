from unittest import TestCase, main, skip
import xarray as xarr
import netCDF4
from pdb import set_trace


class TestXarrConcat(TestCase):
    def test_partial_december_gws(self):
        gravity_wave_december_paths = "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212*006*"

        print("loading data...")
        concat_data = xarr.open_mfdataset(
            gravity_wave_december_paths,
            # NOTE: is this combine throwing things off??? nested...
            concat_dim=["time"],
            combine="nested")
        regular_data = xarr.open_mfdataset(
            gravity_wave_december_paths)

        concat_u = concat_data.variables.get("u")
        regular_u = regular_data.variables.get("u")
        assert (concat_u[0].values == regular_u.values[0]).all()

        print("time concatted data:")
        print(concat_data)

        print("auto concatted data:")
        print(regular_data)
        return

    @ skip
    def test_full_december_gws(self):
        gravity_wave_december_paths = "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212*"

        # TODO: could more intelligently select chunks and time dim
        print("loading data...")
        concat_data = xarr.open_mfdataset(
            gravity_wave_december_paths, concat_dim="time",
            combine="nested")
        regular_data = xarr.open_mfdataset(
            gravity_wave_december_paths)

        response: xarr.DataArray = concat_data["u"]
        level_name = "lev"
        response = response.isel({level_name: 72})

        print("time concatted data:")
        print(concat_data)

        print("auto concatted data:")
        print(regular_data)

        return


if __name__ == "__main__":
    main()
