# test grid
# python -m pytest
# python -m ==> run something as a script

from lattice_fringe.grids import spatial_grid as sg
import numpy as np

sg_grid = sg.SpatialGrid(np.ndarray([1, 2, 3 ,4 ,5]), np.ndarray([1, 2, 3 ,4 ,5]), None)

def test_test():
    assert 1 == 1

# MARK: Spatial grid tests

def test_resize():
    sg_grid_2 = sg_grid.resize(1, (10, 10))
    assert 1 == 1