import numpy as np


class LatticeFringeCompositeImageError(Exception):
    pass


class LatticeFringeDispatchResizeArgsError(Exception):
    pass


def dispatch_resize_args(scale, old_size, new_size):
    if scale is None and new_size is None:
        raise LatticeFringeDispatchResizeArgsError(
            "At least one of 'scale' and 'new_size' must be specified."
        )
    if scale is not None:
        scale = float(scale)
    if isinstance(scale, float):
        scale = [scale, scale]
    if new_size is None:
        new_height = np.round(old_size[0] * scale[0]).astype(int)
        new_width = np.round(old_size[1] * scale[1]).astype(int)
    else:
        new_height = new_size[0]
        new_width = new_size[1]
    return new_height, new_width


def get_composite_image(*args, normalize=True) -> np.ndarray:
    if len(args) == 0:
        raise LatticeFringeCompositeImageError(
            "At least one channel must be specified."
        )
    if len(args) > 3:
        raise LatticeFringeCompositeImageError(
            "At most 3 channels can be specified."
        )
    try:
        if any([a.ndim != 2 for a in args]):
            raise LatticeFringeCompositeImageError(
                "All channels must be 2-dimensional."
            )
    except AttributeError:
        raise LatticeFringeCompositeImageError(
            "All passed channels must be 2-dimensional numpy arrays."
        )
    try:
        if any([a.shape[0] != args[0].shape[0] for a in args]):
            raise LatticeFringeCompositeImageError(
                "All channels must be of the same size."
            )
        if any([a.shape[1] != args[0].shape[1] for a in args]):
            raise LatticeFringeCompositeImageError(
                "All channels must be of the same size."
            )
    except AttributeError:
        raise LatticeFringeCompositeImageError(
            "All passed channels must be 2-dimensional numpy arrays."
        )
    composite = np.zeros((*args[0].shape, 3))
    for k, channel in enumerate(args):
        channel_ = channel.copy()
        if normalize:
            channel_ = channel_ - channel.min()
            channel_ = channel_ / channel_.max()
        composite[:, :, k] = channel_
    return composite


def uniquetol(array: np.ndarray, tolerance: float) -> np.ndarray:
    """ Adapted with corrections from https://stackoverflow.com/questions/
    37847053/uniquify-an-array-list-with-a-tolerance-in-python-uniquetol-
    equivalent. Use only for small 1D arrays.

    """
    eps = np.finfo(array.dtype).resolution
    d = np.abs(array[:, np.newaxis] - array)
    inds = ~(np.triu(d <= tolerance + 2 * eps, 1))
    return array[inds.all(0)]
