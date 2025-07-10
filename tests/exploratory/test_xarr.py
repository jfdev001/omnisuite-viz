from unittest import TestCase, main
import netCDF4  # prevents xarray warning
import xarray as xarr
from pdb import set_trace


class TestXarrayOps(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gravity_wave_files_glob = "data/gravity_waves/*.nc"
        return

    def test_open_mfdataset(self):
        """Automatically concatenates along the time dimension!!"""
        gravity_wave_mfdataset = xarr.open_mfdataset(
            self.gravity_wave_files_glob)
        zonal_wind_var_name = "u"
        u_variable = gravity_wave_mfdataset.variables.get(zonal_wind_var_name)
        t = 0
        u_variable_at_t = u_variable.isel(time=t)
        u_arr = u_variable_at_t.values  # gets raw zonal wind data as array
        dims = u_arr.shape
        lev_dim = dims[0]
        lat_dim = dims[1]
        lon_dim = dims[2]
        expected_lev_dim = 152
        expected_lat_dim = 512
        expected_lon_dim = 1024
        self.assertEqual(lev_dim, expected_lev_dim)
        self.assertEqual(lat_dim, expected_lat_dim)
        self.assertEqual(lon_dim, expected_lon_dim)
        return


if __name__ == "__main__":
    main()
