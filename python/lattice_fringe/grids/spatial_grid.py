import numpy as np

import lattice_fringe.grids.frequency_grid

from lattice_fringe.interfaces import Grid, SpatialUnit
from lattice_fringe.utils import overlay
from lattice_fringe.exceptions import LatticeFringeGridSpecError

import warnings
from typing import Any, Optional, Tuple, Union


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

    def transform(self) -> lattice_fringe.grids.frequency_grid.FrequencyGrid:
        width = self.width
        height = self.height
        return lattice_fringe.grids.frequency_grid.FrequencyGrid(
            np.arange(-width / 2, width / 2) / self.delta_0 / width,
            np.arange(-height / 2, height / 2) / self.delta_1 / height,
            self.unit.transform()
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
