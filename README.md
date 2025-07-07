[![CI](https://github.com/jfdev001/omnisuite-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/jfdev001/omnisuite-examples/actions/workflows/ci.yml) 

# omnisuite-examples

Generate example plots that can be used in OmniSuite.

Currently under development, so use `pip install -e .`.

# usage

The package `omnisuite_examples` is intended to facilitate the generation of plots on a 
[Plate-Carree](https://en.wikipedia.org/wiki/Equirectangular_projection) projection of the Earth for specific 
use with the visualization software `OmniSuite`. 

The workflow (under development) currently involves 
the user defining a concrete configuration class, a concrete grid class, and a concrete animator class.
The configuration class generally defines some plotting parameters, the defaults for which are 
generally suitable for OmniSuite; however, the important bit of the configuration class is that 
it reads in the data and preprocesses it as necessary. The data in general to be plotted will consist
of a latitude array, a longitude array, and a response variable (e.g., temperature, horizontal wind, etc)
with dimensions (time, height, lat, lon). The grid class then gets initialized with these 
lat, lon, and response variables. The user then defines a class inheriting `OmniSuiteWorldMapAnimator` 
and implements `_plot_initial_frame` and `_update_frame` methods. The user can then call the `animate`
method.

An example of this workflow is present at [examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py](https://github.com/jfdev001/omnisuite-examples/blob/main/examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py).
