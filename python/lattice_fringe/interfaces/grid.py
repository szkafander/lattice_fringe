import matplotlib.pyplot as pl
import numpy as np

from lattice_fringe.interfaces.unit import Unit
from lattice_fringe.exceptions import (
    LatticeFringeGridSpecError,
    LatticeFringeDispatchResizeArgsError
)

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union
import warnings


def _dispatch_coords(
    coords_0: np.ndarray,
    coords_1: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    if coords_0.ndim not in [1, 2] or coords_1.ndim not in [1, 2]:
        raise LatticeFringeGridSpecError(
            "x_coords and y_coords must be 1- or 2-dimensional arrays."
        )
    if coords_0.ndim == 1 and coords_1.ndim == 1:
        coords_0, coords_1 = np.meshgrid(coords_0, coords_1)
    return coords_0, coords_1


def _dispatch_resize_args(
    scale: float,
    old_size: Tuple[int, int],
    new_size: Tuple[int, int]
) -> Tuple[int, int]:
    if scale is None and new_size is None:
        raise LatticeFringeDispatchResizeArgsError(
            "At least one of 'scale' and 'new_size' must be specified."
        )
    if scale is not None:
        scale = float(scale)
    if isinstance(scale, float):
        scale = [scale, scale]
    if new_size is None:
        new_height = np.round(old_size[0] * scale[0]).astype(int)
        new_width = np.round(old_size[1] * scale[1]).astype(int)
    else:
        new_height = new_size[0]
        new_width = new_size[1]
    return new_height, new_width


class Grid(ABC):

    def __init__(
        self,
        coords_0: np.ndarray,
        coords_1: np.ndarray,
        unit: Unit
    ) -> None:
        coords_0, coords_1 = _dispatch_coords(coords_0, coords_1)
        self.coords_0 = coords_0
        self.coords_1 = coords_1
        self.unit = unit

    @property
    def axis_0(self) -> np.ndarray:
        return self.coords_0[0, :]

    @property
    def axis_1(self) -> np.ndarray:
        return self.coords_1[:, 0]

    @property
    def extent_0(self) -> np.ndarray:
        return self.axis_0[[0, -1]]

    @property
    def extent_1(self) -> np.ndarray:
        return self.axis_1[[0, -1]]

    @property
    def width(self) -> int:
        return len(self.axis_0)

    @property
    def height(self) -> int:
        return len(self.axis_1)

    @property
    def size(self) -> Tuple[float, float]:
        return self.height, self.width

    @property
    def delta_0(self) -> float:
        return self.axis_0[1] - self.axis_0[0]

    @property
    def delta_1(self) -> float:
        return self.axis_1[1] - self.axis_1[0]

    @property
    @abstractmethod
    def name_0(self) -> str:
        pass

    @property
    @abstractmethod
    def name_1(self) -> str:
        pass

    def __eq__(self, other: "Grid") -> bool:
        if not isinstance(other, self.__class__):
            return False
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            try:
                x_equal = (self.coords_0 == other.coords_0).all()
            except AttributeError:
                return False
            try:
                y_equal = (self.coords_1 == other.coords_1).all()
            except AttributeError:
                return False
        return x_equal and y_equal

    def __getitem__(self, item) -> "Grid":
        if len(item) > 2:
            item = item[:-1]
        return self.__class__(
            self.coords_0.__getitem__(item),
            self.coords_1.__getitem__(item),
            unit=self.unit
        )

    def label_axes(self, axes: Optional[pl.Axes] = None) -> None:
        axes = axes or pl.gca()
        unit = f", {self.unit}" if self.unit else ""
        axes.set_xlabel(f"{self.name_0}, {unit}")
        axes.set_ylabel(f"{self.name_1}, {unit}")

    def resize(
            self,
            scale: Optional[Union[float, Tuple[float]]] = None,
            new_size: Optional[Tuple[int, int]] = None
    ) -> "Grid":
        n_x, n_y = _dispatch_resize_args(scale, self.size, new_size)
        x_axis = np.linspace(self.extent_0[0], self.extent_0[1], n_x)
        y_axis = np.linspace(self.extent_1[0], self.extent_1[1], n_y)
        return self.__class__(
            x_axis,
            y_axis,
            unit=self.unit
        )

    @abstractmethod
    def transform(self, *args, **kwargs) -> "Grid":
        pass

    @abstractmethod
    def plot(self, *args, **kwargs) -> None:
        pass
