import abc
import matplotlib.pyplot as pl
import numpy as np

from typing import Optional, Tuple


class Grid(abc.ABC):

    @abc.abstractproperty
    def coords_0(self) -> np.ndarray:
        pass

    @abc.abstractproperty
    def coords_1(self) -> np.ndarray:
        pass

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

    def label_axes(self, axes: Optional[pl.axes.Axes] = None) -> None:
        axes = axes or pl.gca()
        axes.set_xlabel(
            self.x_name + f", {self.x_unit}" if self.x_unit else "")
        axes.set_ylabel(
            self.y_name + f", {self.y_unit}" if self.y_unit else "")

    @abc.abstractmethod
    def transform(self, *args, **kwargs) -> "Grid":
        pass

    @abc.abstractmethod
    def plot(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def resize(self, *args, **kwargs) -> "Grid":
        pass


class Unit(abc.ABC):

    @abc.abstractproperty
    def base(self, *args, **kwargs) -> "Unit":
        pass

    @abc.abstractproperty
    def multiplier(self, *args, **kwargs) -> int:
        pass
