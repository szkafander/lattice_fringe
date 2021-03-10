import numpy as np


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
