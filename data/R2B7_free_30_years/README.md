# R2B7 Free 30 Year Post-Processed Data

The data in this directory corresponds to post-processed results from 
an [Icosahedral Nonhydrostatic (ICON)](https://www.dwd.de/EN/research/weatherforecasting/num_modelling/01_num_weather_prediction_modells/icon_description.html) 
model run for the years 2019 to 2029.  The model outputs a number of variables such as temperature, wind speeds, humidity, and more (a more complete list of 
what ICON outputs is available in [Appendix A: ICON Model Tutorial 2024](https://www.dwd.de/DE/leistungen/nwv_icon_tutorial/pdf_einzelbaende/icon_tutorial2024.html)). 

The ICON model discretizes the atmosphere both horizontally and vertically
into discrete volumes. While the ICON grid is a complex icosahedral grid whose 
resolution is defined by the `RnBk` (in this case `R2B7`) term, the data in this 
directory correspond to data that has been remapped (this is why the files have 
the `RM` suffix) to a simple latitude-longitude coordinate system. Practically,
you can think of the `RnBk` term as determining the dimensions of a small 
"box" in the atmosphere with length in kilometers given by the 
[formula](https://docs.icon-model.org/buildrun/buildrun_running.html#grid-files)

```python
delta_x = 5050 / (n * 2**k)
```
In this case, the grid resolution for `R2B7` is approximately 20 kilometers. So
if you are looking at Germany from an aerial view, you would see that model 
has divided it into discrete squares---it is squares now because we are looking
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
These "boxes" are not just dividing Germany, however, they are dividing the
entire world as ICON is a global model. This means quantities like temperature,
wind, etc can be predicted in essentially whatever location on Earth you want.
Remember, though, you are still restricted by the fact the resolution is roughly 
20 km, so ICON cannot tell you explicitly what the temperature in a 1 m^3 volume 
above your flat is, for example.

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
since the temperature data was averaged over each month and then over each year
in the 10 year period. This sort of averaging is a common operation in 
climatological studies. To understand this operation, consider the below
roughly constructed table for January in particular where `temperature` is 
some value in Kelvin:

```text
YEAR MONTH   DAY  MODEL_VALUE
2019 January 01   temperature
2019 January 02   temperature
.
.
.
2019 January 31   temperature
2020 January 01   temperature
2020 January 02   temperature
.
.
.
2020 January 31   temperature
```

The first averaging operation taken is over all days in the month for a 
particular year. The result of this operation would be the following table:

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
.
.
.
December temperature
```

and these are the values that are often of interest to climatologists.

These operations are why the time dimension is 12 in the files matching the 
pattern `R2B7*`.

# Inspecting NetCDF Data

In general, you can either inspect NetCDF files using command line tools
like [netCDF-4 64-bit (Windows exe)](https://downloads.unidata.ucar.edu/netcdf/)
(see also [netCDF-4 windows installation instructions](https://pjbartlein.github.io/REarthSysSci/install_netCDF.html)
or the Python interface `netCDF4`.

If you use `ncdump`, then you can call

```shell
ncdump -h PATH_TO_FILE_HERE
```
to get an overview of the variables (see also [`ncdump -h`
documentation](https://www.unidata.ucar.edu/software/netcdf/workshops/2009/utilities/NcdumpHeader.html)).

You could inspect the NetCDF data with Python

```shell
# In a conda environment, make sure you have already called 
# conda install netCDF4 
# if that doesn't work try conda install conda-forge::netcdf4
python
>>> from netCDF4 import Dataset
>>> zonal_wind_dataset = Dataset("R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc")
>>> zonal_wind_dataset.variables
>>> latitude_array = zonal_wind_dataset.variables['lat'][:]
>>> longitude_array = zonal_wind_dataset.variables['lon'][:]
>>> zonal_wind_array = zonal_wind_dataset.variables['u'][:]
>>> # Try looking at the dimensions of these variables, are they what you expect?
>>> # Do they match the `ncdump -h` output?
>>> latitude_array.shape
>>> longitude_array.shape
>>> zonal_wind_array.shape
```
You can find the Python netCDF4 documentation [here](https://unidata.github.io/netcdf4-python/).

Once you have a reasonable understandable of netCDF4 datasets, you can take
a look at what making some simple plots using this data looks like.
For a simple example of what plotting the zonal wind data (i.e.,
the file `R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc`) looks like, 
you can look at the code in 
[icon-visualization-examples/scripts/basic_monthly_zonal_wind_contour.py](https://github.com/jfdev001/icon-visualization-examples/blob/main/scripts/basic_monthly_zonal_wind_contour.py). Follow the installation instructions at 
[icon-visualization-examples/README.md](https://github.com/jfdev001/icon-visualization-examples/tree/main).

Alternatively, you could use `ncview` (installed on WSL, this is the little
penguin icon) or Panoply (this is on your desktop and must be "right clicked"
and run as an admin to work) to inspect NetCDF files without having to do any
coding.

With a grasp of some basic plotting functionality in Python, you can then
think about how to create some animations for OmniGlobe. An example that 
generates 12 frames (one for each month) using the zonal wind data is 
available at [omnisuite_examples/examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py](https://github.com/jfdev001/omnisuite-examples/blob/main/examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py).

Can you generate some animations using the temperature data instead? Can you
upload one of these frames (or all or a subset of them) into the OmniSuite
material editor? If you don't know about OmniSuite yet, don't worry about this step.

The previous dataset you inspected was an average of temperature or zonal wind
over a ten year period for each of the twelve months. You may also inspect 
zonal wind data at a higher temporal resolution by inspecting the files in
`~/AA_intern/climate_datasets/UAICON/remapped`. Higher temporal resolution means
that the scale of the time is in hours instead of in years. There are two types
of files in the `remapped` directory: `GWS` and `BAL`. `GWS` standard for 
gravity waves. `BAL` standards for balanced modes. These files essentially
contain zonal wind data, though the balanced data has been "smoothed". The
files are thus named according to the following formula:

```
<DATA TYPE>_<YEAR><MONTH><DAY>00000<##>.nc
```

where `<DATA TYPE>` is `GWS` or `BAL` and `##` is some arbitrary numbering.
There are 6 hours in between consecutively numbered files. So if you visualize

```
# Data at 00:00 (midnight) on 1 December 2022 
GWS_202212010000053.nc
```

followed by 

```
# Data at 06:00 AM on 1 December 2022 
GWS_202212010000054.nc
```

there is a 6 hour interval between the data contained in the two files.

You can visualize this data with the following 

```
ncview GWS_20221201000005*.nc
```

The `*` means "any other character here". In this case, the above syntax 
gets the following files:

```
GWS_202212010000054.nc
GWS_202212010000055.nc
GWS_202212010000056.nc
GWS_202212010000057.nc
GWS_202212010000058.nc
GWS_202212010000059.nc
```

Try visualizing the `GWS` corresponding to the number `6` followed by any 
other character. Hint: the syntax is very similar to what is already shown
above!

# Windows Subsystem for Linux (WSL) and Bash 

The WSL (assuming it's installed) can be launched with the penguin icon that is
pinned to the taskbar on your windows machine. WSL launches as a terminal 
(also called a command line), which is a simple interface that you can use 
to interact "directly" with the Linux operating system.

You can use programs like `python`, `ncview`, and `ncdump` in the terminal.
When using those programs, make sure that you are in the correct directory 
(aka folder). 

Bash is a programming language that can be used to interact directrly with the
Linux operating through the terminal. The following are some useful bash
commands: 

You can list the contents of the current directory by typing 

```shell
ls
```

You can print your current directory by typing 

```shell 
pwd
```

You can change directories by typing 

```shell
cd PUT_SOME_DIRECTORY_HERE
```

If you do not provide any arguments to `cd`, then by default you will change
to your home directory (i.e., something similar to `/home/ls01`).

You can also change to the previous directory by providing `..` as an argument
to `cd` like

```shell
# if you are in the directory `AA_intern/climate_datasets`
# this command would change you to the directory `AA_intern`
cd ..
```

You can inspect how to use any bash command by typing

```shell 
man BASH_COMMAND
```

like for example

```
man ls
```

For more bash commands, see [Bash cheat
sheet](https://github.com/sudheerj/Linux-cheat-sheet?tab=readme-ov-file#file-and-directory-commands).

# Some Miscellaneous Notes

You can clone git repositories on github using the below command:

```shell
git clone https://some_url_here.git
```

Note, you should use a URL and not something that begins with `git@github.com`.


You can install the necessary packages for a repository by either using
`pip` and a `.venv` OR you can just use `conda`. 

To use `pip` to install packages via a `requirements.txt` file, do the following:

```shell
pip install -r requirements.txt
```

To use `conda` to install packages via `requirements.txt` file, do the following:

```shell
conda install --yes --file requirements.txt
```

You could always install individual packages by calling one of the following:

```shell
pip install <package-name-here>
conda install <package-name-here>
```

You can interactively inspect what's going on in a Python file by using the
Python debugger:

```shell
python -m pdb scripts/some_script.py
```

Here is some documentation for the Python debugger as well as three-note crash
course in its usage:

Very short tutorial: https://www.freecodecamp.org/news/debugging-in-python-using-pdb/

A bit of a longer tutorial: https://realpython.com/python-debugging-pdb/

The actual documentation (it's denser than the tutorials of course, but still good to know about): https://docs.python.org/3/library/pdb.html

You basically need to know the following:

1. You can start debugging your python script with `python -m pdb my_script_name.py` and it enters the script in debug mode. You can then print variables using the `p VARIABLE_NAME` command.  You can set breakpoints in your code by calling `b LINE_NUMBER`. You can list your current break points by calling just `b`. You can list the current line and some surrounding lines at which the debugger has currently stopped by typing `l`. You can execute a single line in your code by call `n` (for next). You can "step into" a line of your code (e.g., if calling a function, the step into will move your debugger "view" into the function) by calling `s`. You can execute the script until you hit a break point by calling `c` for continue.

2. You can instead just `import pdb` at the top of your script and put `pdb.set_trace()` somewhere in your code where you'd like to start debugging. Then if you call `python my_script_name.py` the debugger will automatically start when the python interpreter encounters the line containing the `pdb.set_trace()`.

3. Lastly, you can enter "interactive" mode by typing `interact` while in the debug mode and then you just have a regular python interpreter and not have to worry about accidentally executing the debug commands I listed in point (1). The interactive mode is just like any other interactive mode except you have access to all variables that have been assigned thus far in the script. 

