import numpy as np
import matplotlib.pyplot as pl

from common import Cache, Image, Grid, spatial
from lattice_fringe.interfaces import Filter, FilterBank
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

    def __init__(self, filters: Collection[LogGaborFilter]) -> None:
        self.filters = filters
        frequencies = list(sorted(self.coordinates))
        frequency_multipliers = [frequencies[k+1] / frequencies[k] for k
                                 in np.arange(0, len(frequencies) - 1)]
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
        return [f.get_response(image) for f in self.filters]

    def apply(self, image: Image) -> Image:
        responses = self.get_responses(image)
        return Image(np.dstack(responses), grid=image.grid)

    def get_frequencies(
            self,
            image: Image,
            mode: str = "strongest_vote"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        responses = self.get_responses(image)
        responses = np.dstack(responses)
        center_frequencies = self.frequencies

        if mode == "weighted":
            max_response = np.max(responses, axis=-1)
            term_1 = (self.min_frequency
                      * (1 / np.sum(responses[:, :, :-1], axis=-1)))
            term_2 = np.zeros(responses.shape[:-1])
            for i in range(responses.shape[-1] - 1):
                term_2 = (term_2
                          + self.frequency_multiplier ** ((i - 1) + 0.5)
                          * responses[:, :, i+1])
            frequencies = term_1 * term_2
            channels = responses ** 2
            term_1 = 1 / np.sum(channels[:, :, :-1], axis=-1)
            term_2 = np.zeros(responses.shape[:-1])
            for i in range(responses.shape[-1] - 1):
                term_2 = (term_2
                          + responses[:, :, i] ** 2
                          * self.frequency_multiplier ** ((i - 1) + 0.5)
                          * responses[:, :, i+1] / responses[:, :, i]
                          - frequencies) ** 2
            certainty = 1 / (1 + term_1 * term_2)

        elif mode == "strongest_vote":
            max_response = np.max(responses, axis=-1)
            max_ind = np.argmax(responses, axis=-1)
            neighbor_ind = max_ind + 1
            neighbor_ind[neighbor_ind > responses.shape[-1]] = \
                neighbor_ind[neighbor_ind > responses.shape[-1]] - 1
            this_freqs = center_frequencies[max_ind]
            neighbor_freqs = center_frequencies[neighbor_ind]
            mean_freqs = np.sqrt(this_freqs * neighbor_freqs)
            N = int(np.prod(responses.shape[:-1]))
            idx = np.arange(N) + (neighbor_ind[0:N] - 1) * N
            neighbor_responses = np.reshape(responses[idx],
                                            responses.shape[:-1])
            frequencies = mean_freqs * max_response / neighbor_responses
            certainty = max_response

        else:
            raise ValueError("The argument 'mode' must be 'weighted' or "
                             "'strongest_vote'.")
        return frequencies, certainty, max_response

    def plot(self) -> None:
        pass

    @staticmethod
    def create(
            low_frequency: float = 1.0,
            high_frequency: float = 5.0,
            num_filters: int = 10
    ) -> "LogGaborFilterBank":
        r_multiplier = ((high_frequency / low_frequency)
                        ** (1 / (num_filters - 1)))
        bandwidth = 2 * np.sqrt(2 / np.log(2)) * np.sqrt(np.log(r_multiplier))
        coordinates = [r_multiplier ** (i - 1) * low_frequency for i
                       in range(num_filters)]
        filters = [LogGaborFilter(c, bandwidth) for c in coordinates]
        return LogGaborFilterBank(filters)


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
