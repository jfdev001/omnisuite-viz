[![CI](https://github.com/jfdev001/omnisuite-viz/actions/workflows/ci.yml/badge.svg)](https://github.com/jfdev001/omnisuite-viz/actions/workflows/ci.yml) 

# omnisuite-viz

Generate example plots that can be used in [OmniSuite](https://globoccess.com/omniglobes/).

# installation

Currently under development, so use `pip install -e .`.

# usage

The package `omnisuite_viz` is intended to facilitate the generation of 
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
* Define an `Animator` (you will likely subclass `OmniSuiteWorldMapAnimator`)
  and in particular you should override the `_plot_initial_frame` and 
  `_update_frame` methods.
* Combine these appropriately and then call the `animate` method of `Animator`.
  See `examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py`.
  

You can call 

```python
python examples/plot_timelapsed_icon_r2b7_netcdf_output_on_plate_carree_projection.py -h 
```
to get the help doc for that example.

# Getting Blue Marble Backgrounds

Blue marble backgrounds can be downloaded from https://github.com/jfdev001/cartopy_backgrounds
