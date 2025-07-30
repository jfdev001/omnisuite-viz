#!/usr/bin/bash
# @brief CDO remap of ICON DWD Global to full Gaussian grid
# @todo
#   * support for other remap operations as argument
#     see https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-280001.5
dwd_icon_grib_file=$1
usage="usage: $0 DWD_ICON_GRIB_FILE"
if [[ -z "${dwd_icon_grib_file// }" ]]
then
    echo "$usage"
    exit 1
fi

cdo gennn,F256 icon_grid_0026_R03B07_G.nc F256_weights.nc
cdo -f nc remap,F256,F256_weights.nc $dwd_icon_grib_file ${dwd_icon_grib_file%.grib2}_remapped_F256.nc
