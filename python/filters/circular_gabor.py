import numpy as np

from .. import utils
from ..interfaces import Filter, FilterBank


def circular_gabor_ir(
        f_x: np.ndarray,
        f_y: np.ndarray,
        center_frequency: float,
        sigma: float,
        direction: float
) -> np.ndarray:
    r = np.sqrt(f_x ** 2 + f_y ** 2)
    radial_component = np.exp(-((r - center_frequency) / sigma) ** 2)
    radial_component[np.isnan(radial_component)] = 0
    director = utils.direction_to_director(direction)
    uv = np.dstack((f_x, f_y))
    uv = uv / np.dstack((r, r))
    uv[np.isnan(uv)] = 0
    directional_component = np.sum(
        uv * np.dstack((
            np.ones(f_x.shape) * director[0],
            np.ones(f_x.shape) * director[1]
        )),
        axis=-1
    )
    directional_component[directional_component < 0] = 0
    directional_component = directional_component ** 2
    return radial_component * directional_component
