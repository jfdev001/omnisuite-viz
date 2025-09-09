"""Classes for discrete values of grid and response variable on the grid."""
from abc import ABC, abstractmethod
from numpy import linspace, meshgrid, ndarray
from typing import Tuple, Union
from xarray import DataArray


class Grid(ABC):
    @property
    @abstractmethod
    def mesh(self) -> Tuple[ndarray, ...]:
        raise NotImplementedError


class Grid2D(Grid):
    @property
    @abstractmethod
    def mesh(self) -> Tuple[ndarray, ndarray]:
        raise NotImplementedError


class LatLonGrid(Grid2D):
    @property
    @abstractmethod
    def latitude(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def longitude(self) -> ndarray:
        raise NotImplementedError

    @property
    @abstractmethod
    def response(self) -> Union[ndarray, DataArray]:
        raise NotImplementedError

    @property
    def mesh(self) -> Tuple[ndarray, ndarray]:
        return self.latitude, self.longitude


class WorldMapRectangularGrid(LatLonGrid):
    LONGITUDE_MIN = -180
    LONGITUDE_MAX = 180
    LATITUDE_MIN = -90
    LATITUDE_MAX = 90

    def __init__(
            self,
            longitude_min=LONGITUDE_MIN,
            longitude_max=LONGITUDE_MAX,
            num_longitude_points=360,
            latitude_min=LATITUDE_MIN,
            latitude_max=LATITUDE_MAX,
            num_latitude_points=180):

        assert longitude_min >= self.LONGITUDE_MIN
        assert longitude_max <= self.LONGITUDE_MAX
        assert latitude_min >= self.LATITUDE_MIN
        assert latitude_max <= self.LATITUDE_MAX

        self._longitude = linspace(
            longitude_min, longitude_max, num_longitude_points)

        self._latitude = linspace(
            latitude_min, latitude_max, num_latitude_points)

        self._longitude_mesh, self._latitude_mesh = meshgrid(
            self._longitude, self._latitude)

    @property
    def mesh(self) -> Tuple[ndarray, ndarray]:
        return self._longitude_mesh, self._latitude_mesh

    @property
    def longitude_mesh(self) -> ndarray:
        return self._longitude_mesh

    @property
    def longitude(self) -> ndarray:
        return self._longitude

    @property
    def latitude_mesh(self) -> ndarray:
        return self._latitude_mesh

    @property
    def latitude(self) -> ndarray:
        return self._latitude

    @property
    def response(self):
        """this is really just a placeholder since it's unused in the example"""
        pass


class WorldMapNetcdfGrid(LatLonGrid):
    """Generic world map grid where fields come (expected) from netcdf.

    TODO: A bit misleading to name 'Netcdf' here since the class itself
    is actually agnostic of the data source.
    """
    def __init__(self, response, latitude: ndarray, longitude: ndarray):
        self._latitude = latitude
        self._longitude = longitude
        self._response = response
        return

    @property
    def latitude(self) -> ndarray:
        return self._latitude

    @property
    def longitude(self) -> ndarray:
        return self._longitude

    @property
    def response(self) -> ndarray:
        return self._response
