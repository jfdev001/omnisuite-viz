from abc import ABC, abstractproperty
from numpy import linspace, meshgrid


class Grid(ABC):
    @abstractproperty
    def grid(self):
        pass


class Globe(Grid):
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

        self._longitude = linspace(
            longitude_min, longitude_max, num_longitude_points)

        self._latitude = linspace(
            latitude_min, latitude_max, num_latitude_points)

    def grid(self):
        return
