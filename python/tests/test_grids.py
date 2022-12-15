# test grid
# python -m pytest
# python -m ==> run something as a script

import numpy as np
import pytest

from lattice_fringe.grids import SpatialGrid


# TODO - how to test for parameter combinations?
@pytest.fixture
def _x0():
    return np.arange(5)


@pytest.fixture
def _x1():
    return np.arange(0, 7, 2)

@pytest.fixture(name="bg")
def basic_grid(_x0, _x1):
    return SpatialGrid(_x0, _x1, "unit")

# TODO: Check this idea to solve the parameter combinations problem (sketch)
def test_grid_axes():
    errors = []

    x0_arr = [[np.arange(2), [0, -1]],
              [np.arange(5), [0, -1, 2, 3, 4]],
              [np.arange(6), [0, -1, 2, 3, 4, 5]]]

    for elem in x0_arr:
        sg = SpatialGrid(elem[0], np.arange(1), "unit")
        
        if not np.array_equal(sg.axis_0, elem[1]):
            errors.append(str(sg.axis_0)+"is not equal to "+str(elem[1]))
    
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_grid_names(bg):
    assert (bg.name_0, bg.name_1) == ("x", "y")

def test_grid_axis_0(bg, request):
    print(request)
    assert np.array_equal(bg.axis_0, [0, 1, 2, 3, 4])


def test_grid_axis_1(bg):
    assert np.array_equal(bg.axis_1, [0, 2, 4, 6])


def test_grid_deltas(bg):
    assert (bg.delta_0, bg.delta_1) == (1, 2)


def test_grid_extent_0(bg):
    assert np.array_equal(bg.extent_0, [0, 4])


def test_grid_extent_1(bg):
    assert np.array_equal(bg.extent_1, [0, 6])


def test_grid_width_height(bg):
    assert (bg.width, bg.height) == (5, 4)