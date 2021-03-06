import numpy as np
import matplotlib.pyplot as pl

from common import Cache, Image, Grid, spatial
from interfaces import Filter, FilterBank
from utils import (
    get_impulse_response_components,
    absolute_response,
    overlay,
    uniquetol
)

from typing import Collection, Optional, Tuple


_CACHE_ATTRS = ("kernel_right", "kernel_left", "grid")


def log_gabor_ir(
        f_x: np.ndarray,
        f_y: np.ndarray,
        center_frequency: float,
        bandwidth: float,
        direction: float
) -> np.ndarray:
    cb = 4 / (bandwidth ** 2 * np.log(2))
    r, d = get_impulse_response_components(f_x, f_y, direction)
    radial_component = np.exp(- cb * np.log(r / center_frequency) ** 2)
    radial_component[np.isnan(radial_component)] = 0
    return radial_component * d


def circular_gabor_ir(
        f_x: np.ndarray,
        f_y: np.ndarray,
        center_frequency: float,
        sigma: float,
        direction: float
) -> np.ndarray:
    r, d = get_impulse_response_components(f_x, f_y, direction)
    radial_component = np.exp(-((r - center_frequency) / sigma) ** 2)
    radial_component[np.isnan(radial_component)] = 0
    return radial_component * d


class LogGaborFilter(Filter):

    def __init__(self, center_frequency: float, bandwidth: float) -> None:
        self.center_frequency = center_frequency
        self.bandwidth = bandwidth
        self._cache = Cache(*_CACHE_ATTRS)

    @property
    def coordinate(self) -> float:
        return self.center_frequency

    def get_kernels(
            self,
            image: Optional[Image] = None,
            grid: Optional[Grid] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if image is not None:
            grid = image.grid
        elif grid is None:
            r = self.center_frequency * 2
            x, y = np.mesgrid(
                np.linspace(-r, r, 100),
                np.linspace(-r, r, 100)
            )
            grid = Grid(x, y, "domain", spatial)

        # if grid in cache, pull from there
        if grid == self._cache.grid:
            kernel_right = self._cache.kernel_right
            kernel_left = self._cache.kernel_left
        else:
            kernel_right = log_gabor_ir(
                grid.x_coords,
                grid.y_coords,
                self.center_frequency,
                self.bandwidth,
                0
            )
            kernel_left = log_gabor_ir(
                grid.x_coords,
                grid.y_coords,
                self.center_frequency,
                self.bandwidth,
                np.pi / 2
            )
            self._cache.kernel_right = kernel_right
            self._cache.kernel_left = kernel_left
            self._cache.grid = grid
        return kernel_right, kernel_left

    def get_response(self, image: Image) -> np.ndarray:
        if image.domain == spatial:
            image = image.ft()
        kernel_right, kernel_left = self.get_kernels(image)
        response_right = absolute_response(image.channels, kernel_right)
        response_left = absolute_response(image.channels, kernel_left)
        return response_right + response_left

    def apply(self, image: Image) -> Image:
        if image.domain == spatial:
            image = image.ft()
            grid_spatial = image.grid
        else:
            grid_spatial = image.grid.ift()
        return Image(self.get_response(image), grid=grid_spatial)

    def plot(
            self,
            image: Optional[Image] = None,
            grid: Optional[Grid] = None
    ) -> None:
        if image is not None:
            grid = image.grid
        elif grid is None:
            raise ValueError("Provide either an image or a grid.")
        if grid.domain == spatial:
            grid = grid.ft()
        kernel_right, kernel_left = self.get_kernels(grid)
        pl.imshow(overlay(kernel_right, kernel_left))


class LogGaborFilterBank(FilterBank):

    def __init__(self, filters) -> None:
        self.filters = filters
        frequencies = list(sorted(self.coordinates))
        frequency_multipliers = [frequencies[k+1] / frequencies[k] for k
                                 in np.arange(1, len(frequencies))]
        frequency_multiplier = uniquetol(np.array(frequency_multipliers), 1e-5)
        if len(frequency_multiplier) > 1:
            raise ValueError("The frequency multiplier cannot be inferred. "
                             "Consider using the 'create' method to "
                             "instantiate this class.")
        super(LogGaborFilterBank, self).__init__(
            filters,
            ("center_frequency",)
        )
        self.frequency_multiplier = frequency_multiplier

    @property
    def frequencies(self) -> Collection:
        """ Alias for coordinates. """
        return self.coordinates

    @property
    def min_frequency(self) -> float:
        return min(self.frequencies)

    def get_responses(self, image: Image) -> Collection:
        pass

    def apply(self, image: Image) -> Image:
        pass

    def get_frequencies(
            self,
            image: Image
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        pass

    def plot(self) -> None:
        pass

    @staticmethod
    def create(
            low_frequency: float = 1.0,
            high_frequency: float = 5.0,
            num_filters: int = 10
    ) -> "LogGaborFilterBank":
        pass


class CircularGaborFilter(Filter):

    def __init__(self, center_frequency: float, bandwidth: float) -> None:
        self.center_frequency = center_frequency
        self.bandwidth = bandwidth
        self._cache = None

    @property
    def coordinate(self) -> float:
        return self.center_frequency

    def get_kernels(
            self,
            image: Optional[Image] = None,
            grid: Optional[Grid] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        pass

    def get_response(self, image: Image) -> np.ndarray:
        pass

    def apply(self, image: Image) -> Image:
        pass

    def plot(self) -> None:
        pass


class CircularGaborFilterBank(FilterBank):

    @property
    def min_frequency(self) -> float:
        return min(self.coordinates)

    def get_responses(self, image: Image) -> Collection:
        pass

    def apply(self, image: Image) -> Image:
        pass

    def get_frequencies(
            self,
            image: Image
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        pass

    def plot(self) -> None:
        pass

    @staticmethod
    def create(
            low_frequency: float = 1.0,
            high_frequency: float = 5.0,
            num_filters: int = 10
    ) -> "CircularGaborFilterBank":
        pass
