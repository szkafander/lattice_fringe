import numpy as np

from ..common import Image, Grid
from ..interfaces import Filter, FilterBank
from ..utils import get_impulse_response_components

from typing import Collection, Optional, Tuple


def impulse_response(
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


class LogGaborFilter(Filter):

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


class LogGaborFilterBank(FilterBank):

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
    ) -> "LogGaborFilterBank":
        pass
