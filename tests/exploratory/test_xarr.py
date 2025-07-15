from unittest import TestCase, main, skip, skipIf
import netCDF4  # prevents xarray warning
import xarray as xarr
from os.path import exists
try:
    from metpy.calc import geopotential_to_height
    from metpy.units import units
    skip_geopotential_to_height_test = False
except ModuleNotFoundError:
    skip_geopotential_to_height_test = True

from pdb import set_trace


class TestXarrayOps(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gravity_wave_files_glob = "data/gravity_waves/*.nc"
        cls.gravity_waves_files = [
            "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212010000060.nc",
            "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212010000061.nc"
        ]
        cls.gravity_wave_levante_files_glob = "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212*006*"
        cls.local_gravity_wave_file = "data/gravity_waves/GWS_202603010000053.nc"
        cls.levante_gravity_wave_file = "/work/bm1233/m300685/UAICON/modes/inverse/GWS_202212010000060.nc"
        return

    def test_open_mfdataset_on_files(self):
        """open files list"""
        mfdataset = xarr.open_mfdataset(self.gravity_waves_files)
        return

    def test_open_mfdataset_on_levante_glob(self):
        """open levante gwave glob"""
        mfdataset = xarr.open_mfdataset(self.gravity_wave_levante_files_glob)
        return

    def test_open_mfdataset_on_file(self):
        """open single file"""
        gravity_wave_single_mfdatset = xarr.open_mfdataset(
            self.local_gravity_wave_file)
        shape = list(gravity_wave_single_mfdatset.sizes.values())
        time_dim = shape[0]
        expected_time_dim = 1
        self.assertEqual(time_dim, expected_time_dim)
        return

    @skipIf(skip_geopotential_to_height_test, "metpy not found")
    def test_geopotential_height_to_geometric_height(self):
        """Convert geopotential height to geometric height"""
        if exists(self.local_gravity_wave_file):
            gravity_wave_file = self.local_gravity_wave_file
        elif exists(self.levante_gravity_wave_file):
            gravity_wave_file = self.levante_gravity_wave_file
        gravity_wave_single_mfdatset = xarr.open_mfdataset(gravity_wave_file)
        geopotential_height_var_name = "Z"
        geopotential_height = (
            gravity_wave_single_mfdatset
            .variables
            .get(geopotential_height_var_name)
            .values
        )

        # geopot_height = geopot/g0 --> geopot_height*g0 = geopot
        # TODO: ... but this not yielding values in the expected range...
        # known max altitude is ~ 120km 
        STANDARD_GRAVITY: float = 9.80665
        geopotential = geopotential_height * STANDARD_GRAVITY
        geopotential_quantities = units.Quantity(geopotential, "m^2/s^2")

        geometric_height = geopotential_to_height(geopotential_quantities)
        set_trace()

        return

    def test_open_mfdataset_on_glob(self):
        """Open on glob Automatically concatenates along the time dimension!!"""
        gravity_wave_mfdataset = xarr.open_mfdataset(
            self.local_gravity_wave_files_glob)
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
