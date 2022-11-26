import matplotlib.pyplot as pl
import matplotlib.axes as ax
import numpy as np
import utils
import warnings

from lattice_fringe.common.axes import Axes, pixel_axes, pixel_frequency_axes
from lattice_fringe.common.domain import Domain, spatial, frequency
from lattice_fringe.common.utils import dispatch_resize_args

from typing import Optional, Tuple, Union


class LatticeFringeGridError(Exception):
    pass


class LatticeFringeGridSpecError(LatticeFringeGridError):
    pass


class LatticeFringeGridFTError(LatticeFringeGridError):
    pass


class Grid:

    def __init__(
            self,
            x_coords: np.ndarray,
            y_coords: np.ndarray,
            axes: Axes = pixel_axes,
            domain: Domain = spatial
    ) -> None:
        if x_coords.ndim not in [1, 2] or y_coords.ndim not in [1, 2]:
            raise LatticeFringeGridSpecError(
                "x_coords and y_coords must be 1- or 2-dimensional arrays."
            )
        if x_coords.ndim == 1 and y_coords.ndim == 1:
            x_coords, y_coords = np.meshgrid(x_coords, y_coords)
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.axes = axes
        self.domain = domain

    def __eq__(self, other: "Grid") -> bool:
        if not isinstance(other, Grid):
            return False
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            try:
                x_equal = (self.x_coords == other.x_coords).all()
            except AttributeError:
                return False
            try:
                y_equal = (self.y_coords == other.y_coords).all()
            except AttributeError:
                return False
        return self.domain == other.domain and x_equal and y_equal

    def __getitem__(self, item) -> "Grid":
        """
        Grid objects can be indexed using numpy array indexing syntax.
        N-dimensional slices will be converted to 2-dimensional slices.

        :param item: The requested item, i.e., an index, slice, mask, etc. All
            valid numpy indexing methods are accepted.
        :return: A subset of the Grid object.

        """
        # make the slice 2-dimensional if needed
        if len(item) > 2:
            item = item[:-1]
        return Grid(
            self.x_coords.__getitem__(item),
            self.y_coords.__getitem__(item),
            axes=self.axes,
            domain=self.domain
        )

    @property
    def x_axis(self) -> np.ndarray:
        return self.x_coords[0, :]

    @property
    def y_axis(self) -> np.ndarray:
        return self.y_coords[:, 0]

    @property
    def x_extent(self) -> np.ndarray:
        return self.x_axis[[0, -1]]

    @property
    def y_extent(self) -> np.ndarray:
        return self.y_axis[[0, -1]]

    @property
    def width(self) -> int:
        return len(self.x_axis)

    @property
    def height(self) -> int:
        return len(self.y_axis)

    @property
    def size(self) -> Tuple[float, float]:
        return self.height, self.width

    @property
    def x_delta(self) -> float:
        return self.x_axis[1] - self.x_axis[0]

    @property
    def y_delta(self) -> float:
        return self.y_axis[1] - self.y_axis[0]

    def ft(self) -> "Grid":
        if self.domain == frequency:
            raise LatticeFringeGridFTError(
                "This grid is already frequency-domain. Fourier transforming "
                "is not meaningful."
            )
        n_x = self.width
        n_y = self.height
        return Grid(
            np.arange(-n_x / 2, n_x / 2) / self.x_delta / n_x,
            np.arange(-n_y / 2, n_y / 2) / self.y_delta / n_y,
            axes=frequency.transform_axes_to(self.axes, spatial),
            domain=frequency
        )

    def ift(self) -> "Grid":
        xr = self.x_extent[1] - self.x_extent[0]
        yr = self.y_extent[1] - self.y_extent[0]
        if x_name[-10:] == " frequency":
            x_name = x_name[1:]
        if y_name[-10:] == " frequency":
            y_name = y_name[1:]
        if x_unit[:2] == "1/":
            x_unit = x_unit[2:]
        if y_unit[:2] == "1/":
            y_unit = y_unit[2:]
        return Grid(
            np.linspace(0, xr, len(self.x_axis)),
            np.linspace(0, yr, len(self.y_axis)),
            axes=spatial.transform_axes_to(self.axes, frequency)
        )

    def resize(
            self,
            scale: Optional[Union[float, Tuple[float]]] = None,
            new_size: Optional[Tuple[int, int]] = None
    ) -> "Grid":
        n_x, n_y = dispatch_resize_args(scale, self.size, new_size)
        x_axis = np.linspace(self.x_extent[0], self.x_extent[1], n_x)
        y_axis = np.linspace(self.y_extent[0], self.y_extent[1], n_y)
        return Grid(
            x_axis,
            y_axis,
            x_unit=self.x_unit,
            y_unit=self.y_unit,
            domain=self.domain
        )

    def label_axes(self, axes: Optional[ax.Axes] = None) -> None:
        axes = axes or pl.gca()
        axes.set_xlabel(
            self.x_name + f", {self.x_unit}" if self.x_unit else "")
        axes.set_ylabel(
            self.y_name + f", {self.y_unit}" if self.y_unit else "")

    def plot(self) -> None:
        xx = self.x_coords / np.abs(self.x_coords).max()
        yy = self.y_coords / np.abs(self.y_coords).max()
        c = xx
        m = -xx
        y = yy
        pl.imshow(
            utils.overlay(c, m, y),
            extent=(*self.x_extent, *self.y_extent)
        )
        self.label_axes()
