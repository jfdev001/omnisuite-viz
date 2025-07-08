# R2B7 Free 30 Year Post-Processed Data

The data in this directory corresponds to post-processed results from 
an [Icosahedral Nonhydrostatic (ICON)](https://www.dwd.de/EN/research/weatherforecasting/num_modelling/01_num_weather_prediction_modells/icon_description.html) 
model run for the years 2019 to 2029.  The model outputs a number of variables such as temperature, wind speeds, humidity, and more (a more complete list of 
what ICON outputs is available in [Appendix A: ICON Model Tutorial 2024](https://www.dwd.de/DE/leistungen/nwv_icon_tutorial/pdf_einzelbaende/icon_tutorial2024.html)). 

The ICON model discretizes the atmosphere both horizontally and vertically
into discrete volumes. While the ICON grid is a complex icosahedral grid whose 
resolution is defined by the `RnBk` term, the data in this directory
correspond to data that has been remapped (this is why the files have the 
`RM` suffix) to a simple latitude-longitude coordinate system. Practically,
you can think of the `RnBk` term as determining the dimensions of a small 
"box" in the atmosphere with length in kilometers given by the 
[formula](https://docs.icon-model.org/buildrun/buildrun_running.html#grid-files)

```python
delta_x = 5050 / (n * 2**k)
```
In this case, the grid resolution for `R2B7` is approximately 20 kilometers. So
you are looking at Germany from an aerial view, you would see that it is 
divided into discrete squares---it is squares now because we are looking
from above, so we see only the top of our "boxes"---with dimensions as below

```text
-------------
|           |
|           |
|           |
|           |
-------------
^           ^
|___________|
      |
    20 km
```

The files `R2B7_free_30_years_temp-atm_3d_ML_ymonmean_2019-2029_RM.nc`
and `R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc` are the ICON
model output data stored in [netCDF4](https://unidata.github.io/netcdf4-python/)
format, which is a particularly convenient format for storing multidimensional
and irregularly shaped data that exist in geoinformatics. The file
`R2B7_free_30_years_temp-atm_3d_ML_ymonmean_2019-2029_RM.nc` stores temperature
data at various height levels in the atmosphere. The file 
`R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc` stores zonal wind
(this is the horizontal wind component, i.e., wind moving from "left" to "right"
or "right" to "left" in the atmosphere) also at various height levels in the
atmosphere. The file `hfile.nc` provides information about the vertical
discretization. In particular, the variable `z_mc` in `hfile.nc` for a given
latitude and longitude corresponds to some height in meters at which the value 
of a variable such as zonal wind `u` in 
`R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc` is present.


The file `R2B7_free_30_years_temp-atm_3d_ML_ymonmean_2019-2029_RM.nc` has 
temperature data of the shape `(time, height, lat, lon)` where `time = 12`
since the temperature data averaged over each month and then over each year
in the 10 year period. This sort of averaging is a common operation in 
climatological studies. To understand this operation, consider the below
roughly constructed table where `temperature` is some value in Kelvin:

```text
YEAR MONTH   DAY  MODEL_VALUE
2019 January 01   temperature
2019 January 02   temperature
...
2019 January 31   temperature
2020 January 01   temperature
2020 January 02   temperature
...
2020 January 31   temperature
```

The first averaging operation taken is over all days in the month for a 
particular year. The result of this operation would be the following:

```text
YEAR MONTH   AVERAGE_MODEL_VALUE_OVER_DAYS_IN_MONTH
2019 January temperature
2020 January temperature
```

Then if you want to see how the value of january varies over the course of
years 2019 and 2020, you could then average over years and recover the 
following table:

```text
MONTH   AVERAGE_MODEL_VALUE_OVER_YEARS_2019_to_2020
January temperature
```

If you do this for all months, then you end up with a result like

```text
MONTH    AVERAGE_MODEL_VALUE_OVER_YEARS_2019_to_2020
January  temperature
February temperature
...
December temperature
```

and these are the values that are often of interest to climatologists.

These operations are why the time dimension is 12 in the files matching the 
pattern `R2B7*`.

In general, you can either inspect netCDF files using command line tools
like [netCDF-4 64-bit (bWindows exe)](https://downloads.unidata.ucar.edu/netcdf/)
(see also [netCDF-4 windows installation instructions](https://pjbartlein.github.io/REarthSysSci/install_netCDF.html)
or the Python interface `netCDF4`.

For a simple example of what plotting the zonal wind data (i.e.,
the file `R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc`) looks like, 
you can look at the code in 
[icon-visualization-examples/scripts/basic_monthly_zonal_wind_contour.py](https://github.com/jfdev001/icon-visualization-examples/blob/main/scripts/basic_monthly_zonal_wind_contour.py). Follow the installation instructions at 
[icon-visualization-examples/README.md](https://github.com/jfdev001/icon-visualization-examples/tree/main).
