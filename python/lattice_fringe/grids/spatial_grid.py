from __future__ import annotations

import matplotlib.pyplot as pl
import numpy as np

from lattice_fringe.interfaces import Grid, SpatialUnit
from lattice_fringe.utils import get_composite

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lattice_fringe.grids.frequency_grid import FrequencyGrid


class SpatialGrid(Grid):

    def __init__(
            self,
            coords_0: np.ndarray,
            coords_1: np.ndarray,
            unit: SpatialUnit
    ) -> None:
        super(SpatialGrid, self).__init__(coords_0, coords_1, unit)

    def transform(self) -> FrequencyGrid:
        from lattice_fringe.grids.frequency_grid import FrequencyGrid
        width = self.width
        height = self.height
        return FrequencyGrid(
            np.arange(-width / 2, width / 2) / self.delta_0 / width,
            np.arange(-height / 2, height / 2) / self.delta_1 / height,
            self.unit.transform()
        )

    def plot(self) -> None:
        x = self.coords_0 / np.abs(self.coords_0).max()
        y = self.coords_1 / np.abs(self.coords_1).max()
        pl.imshow(
            get_composite(x, -x, y),
            extent=(*self.extent_0, *self.extent_1)
        )
        self.label_axes()
