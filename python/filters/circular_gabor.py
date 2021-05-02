import numpy as np

from ..interfaces import Filter, FilterBank
from ..utils import get_impulse_response_components


def impulse_response(
        f_x: np.ndarray,
        f_y: np.ndarray,
        center_frequency: float,
        sigma: float,
        direction: float
) -> np.ndarray:
    r, d = get_impulse_response_components(f_x, f_y, direction)
    radial_component = np.exp(-((r - center_frequency) / sigma) ** 2)
    radial_component[np.isnan(radial_component)] = 0
    return radial_component * d
