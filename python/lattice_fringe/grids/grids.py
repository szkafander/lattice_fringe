# import matplotlib.pyplot as pl
# import matplotlib.axes as ax
# import numpy as np
# import utils

# from lattice_fringe.common.axes import Axes, pixel_axes, pixel_frequency_axes
# from lattice_fringe.common.domain import Domain, spatial, frequency
# from lattice_fringe.common.utils import dispatch_resize_args


class LatticeFringeGridError(Exception):
    pass


class LatticeFringeGridSpecError(LatticeFringeGridError):
    pass


class LatticeFringeDispatchResizeArgsError(LatticeFringeGridError):
    pass


# class LatticeFringeGridFTError(LatticeFringeGridError):
#     pass

import numpy as np

from lattice_fringe.interfaces import Grid, SpatialUnit
from lattice_fringe.utils import overlay

import warnings
from typing import Any, Optional, Tuple, Union


def _dispatch_resize_args(scale, old_size, new_size):
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


class SpatialGrid(Grid):

    def __init__(
            self,
            coords_0: np.ndarray,
            coords_1: np.ndarray,
            unit: SpatialUnit
    ) -> None:
        if coords_0.ndim not in [1, 2] or coords_1.ndim not in [1, 2]:
            raise LatticeFringeGridSpecError(
                "x_coords and y_coords must be 1- or 2-dimensional arrays."
            )
        if coords_0.ndim == 1 and coords_1.ndim == 1:
            coords_0, coords_1 = np.meshgrid(coords_0, coords_1)
        self.coords_0 = coords_0
        self.coords_1 = coords_1
        self.unit = unit

    def __eq__(self, other: "Grid") -> bool:
        if not isinstance(other, SpatialGrid):
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
            self.coords_0.__getitem__(item),
            self.coords_1.__getitem__(item),
            axes=self.axes,
            domain=self.domain
        )

    def transform(self) -> Any:
        width = self.width
        height = self.height
        return FrequencyGrid(
            np.arange(-width / 2, width / 2) / self.delta_0 / width,
            np.arange(-height / 2, height / 2) / self.delta_1 / height,
            self.unit.transform()
        )

    def resize(
            self,
            scale: Optional[Union[float, Tuple[float]]] = None,
            new_size: Optional[Tuple[int, int]] = None
    ) -> "Grid":
        n_x, n_y = _dispatch_resize_args(scale, self.size, new_size)
        x_axis = np.linspace(self.extent_0[0], self.extent_0[1], n_x)
        y_axis = np.linspace(self.extent_1[0], self.extent_1[1], n_y)
        return SpatialGrid(
            x_axis,
            y_axis,
            unit=self.unit
        )

    def plot(self) -> None:
        import matplotlib.pyplot as pl
        xx = self.coords_0 / np.abs(self.coords_0).max()
        yy = self.coords_1 / np.abs(self.coords_1).max()
        c = xx
        m = -xx
        y = yy
        pl.imshow(
            overlay(c, m, y),
            extent=(*self.extent_0, *self.extent_1)
        )
        self.label_axes()
