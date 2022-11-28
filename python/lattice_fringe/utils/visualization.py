import numpy as np


def normalize(array: np.ndarray) -> np.ndarray:
    array = array - array.min()
    return array / array.max()


def get_composite(
    *channels: np.ndarray,
    normalize: bool = True
) -> np.ndarray:
    if len(channels) == 0:
        raise ValueError("At least one channel must be specified.")
    if len(channels) > 3:
        raise ValueError("At most 3 channels can be specified.")
    try:
        if any([a.ndim != 2 for a in channels]):
            raise ValueError("All channels must be 2-dimensional.")
    except AttributeError:
        raise ValueError("All passed channels must be 2-dimensional numpy "
                         "arrays.")
    try:
        if any([a.shape[0] != channels[0].shape[0] for a in channels]):
            raise ValueError("All channels must be of the same size.")
        if any([a.shape[1] != channels[0].shape[1] for a in channels]):
            raise ValueError("All channels must be of the same size.")
    except AttributeError:
        raise ValueError("All passed channels must be 2-dimensional numpy "
                         "arrays.")
    composite = np.zeros((*channels[0].shape, 3))
    for k, channel in enumerate(channels):
        if normalize:
            composite[:, :, k] = normalize(channel.copy())
        else:
            composite[:, :, k] = channel.copy()
    return composite
