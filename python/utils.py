import numpy as np

from typing import Tuple


def overlay(*args, normalize=True) -> np.ndarray:
    if len(args) == 0:
        raise ValueError("At least one channel must be specified.")
    if len(args) > 3:
        raise ValueError("At most 3 channels can be specified.")
    try:
        if any([a.ndim != 2 for a in args]):
            raise ValueError("All channels must be 2-dimensional.")
    except AttributeError:
        raise ValueError("All passed channels must be 2-dimensional numpy "
                         "arrays.")
    try:
        if any([a.shape[0] != args[0].shape[0] for a in args]):
            raise ValueError("All channels must be of the same size.")
        if any([a.shape[1] != args[0].shape[1] for a in args]):
            raise ValueError("All channels must be of the same size.")
    except AttributeError:
        raise ValueError("All passed channels must be 2-dimensional numpy "
                         "arrays.")
    composite = np.zeros((*args[0].shape, 3))
    for k, channel in enumerate(args):
        channel_ = channel.copy()
        if normalize:
            channel_ = channel_ - channel.min()
            channel_ = channel_ / channel_.max()
        composite[:, :, k] = channel_
    return composite


def direction_to_director(direction: float) -> Tuple:
    return np.cos(direction), np.sin(direction)


def get_radial_component(f_x: np.ndarray, f_y: np.ndarray) -> np.ndarray:
    return np.sqrt(f_x ** 2 + f_y ** 2)


def get_impulse_response_components(
        f_x: np.ndarray,
        f_y: np.ndarray,
        direction: float
) -> Tuple[np.ndarray, np.ndarray]:
    r = get_radial_component(f_x, f_y)
    director = direction_to_director(direction)
    uv = np.dstack((f_x, f_y))
    uv = uv / np.dstack((r, r))
    uv[np.isnan(uv)] = 0
    d = np.sum(
        uv * np.dstack((
            np.ones(f_x.shape) * director[0],
            np.ones(f_x.shape) * director[1]
        )),
        axis=-1
    )
    d[d < 0] = 0
    d = d ** 2
    return r, d


def absolute_response(f_1: np.ndarray, f_2: np.ndarray) -> np.ndarray:
    return np.abs(np.fft.ifft2(np.fft.fftshift(f_1 * f_2)))
