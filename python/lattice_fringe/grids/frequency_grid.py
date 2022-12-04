from __future__ import annotations

import matplotlib.pyplot as pl
import numpy as np

from lattice_fringe.interfaces import Grid, FrequencyUnit
from lattice_fringe.utils import get_composite

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lattice_fringe.grids.spatial_grid import SpatialGrid


class FrequencyGrid(Grid):

    def __init__(
            self,
            coords_0: np.ndarray,
            coords_1: np.ndarray,
            unit: FrequencyUnit
    ) -> None:
        super(FrequencyGrid, self).__init__(coords_0, coords_1, unit)

    def transform(self) -> SpatialGrid:
        xr = self.extent_0[1] - self.extent_0[0]
        yr = self.extent_1[1] - self.extent_1[0]
        return SpatialGrid(
            np.linspace(0, xr, len(self.x_axis)),
            np.linspace(0, yr, len(self.y_axis)),
            axes=self.unit.transform()
        )

    def plot(self) -> None:
        x = self.coords_0 / np.abs(self.coords_0).max()
        y = self.coords_1 / np.abs(self.coords_1).max()
        pl.imshow(
            get_composite(x, -x, y),
            extent=(*self.extent_0, *self.extent_1)
        )
        self.label_axes()
