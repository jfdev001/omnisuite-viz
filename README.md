[![CI](https://github.com/jfdev001/omnisuite-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/jfdev001/omnisuite-examples/actions/workflows/ci.yml) 

# omnisuite-examples

Generate example plots that can be used in [OmniSuite](https://globoccess.com/omniglobes/).

# installation

## On Linux/Unix

Regardless of whether you wish to develop, run the examples, or use the 
`omnisuite-examples` package as a dependency in a Python package, you will
need to first clone the repository.

```shell
cd ~/
git clone https://github.com/jfdev001/omnisuite-examples.git
```

If you wish only to use `omnisuite-examples` as a dependency in a Python package
that you are developing and NOT run the examples, then do the following:

```shell
path_to_my_python_pkg="path/to/my-py-pkg"
cd $path_to_my_python_pkg
pip install ~/omnisuite-examples 
```

If you wish to develop/contribute to `omnisuite-examples` AND/OR run the 
examples, then do the following:

```shell
cd ~/omnisuite-examples
python3 -m venv .venv  
source .venv/bin/activate # or use `direnv allow .` if you have direnv installed
pip install -r requirements-dev.txt  
pip install -e .
``` 

## Docker

TODO: Provide instructions here for windows users.

# usage

The package `omnisuite_examples` is intended to facilitate the generation of 
plots on a [Plate-Carree](https://en.wikipedia.org/wiki/Equirectangular_projection) 
projection of the Earth for specific use with the visualization software 
OmniSuite

The tentative workflow currently involves the following steps:
* Define a `Reader` (you will need to subclass it) that reads your 
  netcdf/grib data and post processes it into a `LatLonGrid`.
    * The `LatLonGrid` (you will likely use the concrete implementation 
     `WorldMapNetcdfGrid`) has `longitude`, `latitude`, and `response` 
      properties (aka member data) where the `response` is a variable like 
      zonal wind, temperature, etc.
* Define an `AnimatorConfig` (you will likely use the `NetcdfAnimatorConfig`) 
  that stores general information like the 
  resolution of your frames in the animation, output directory for animation, 
  file name format for frames (e.g., png, jpg), as well as the number of 
  frames in the animation itself (e.g., could be 365 frames if you have 
  365 days of wind data on the globe that you wish to animate, could be 12
  frames if you only have 12 months of temperature data you wish to animate,
  etc.).
* Define an `Animator` (you will should subclass `OmniSuiteWorldMapAnimator`)
  and in particular you should override the `_plot_initial_frame` and 
  `_update_frame` methods.
* Combine these appropriately and then call the `animate` method of `Animator`.
  See `examples/` for example workflows.

In order of increasing complexity, you may look at the following examples
to get an idea for how to implement the above workflow:

```shell
# Arbitrary number of frame animation for artifical data on world map
python examples/plot_timelapsed_perlin_noise_on_plate_carree_projection.py -h

# Read 12 month low res zonal wind/temperature r2b7 netcdf data and make animation
# where each frame is the response variable plotted on the world map for a given
# month 
python examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py -h

# Read higher res gravity wave/balanced netcdf data using xarray and plot on 
# world map
# TODO:
python examples/plot_timelapsed_
```
