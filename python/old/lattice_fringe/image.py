import matplotlib.pyplot as pl
import numpy as np

from lattice_fringe.common.domain import Domain, spatial, frequency
from lattice_fringe.common.grid import Grid
from lattice_fringe.common.utils import dispatch_resize_args

from imageio import imread
from scipy.fft import fft2, fftshift, ifft2
from skimage.color import rgb2gray, rgba2rgb
from skimage.transform import resize

from typing import Optional, Tuple, Union


class LatticeFringeImageError(Exception):
    pass


class LatticeFringeImageSpecError(LatticeFringeImageError):
    pass


class LatticeFringeImageFTError(LatticeFringeImageError):
    pass


class LatticeFringeImageIOError(LatticeFringeImageError):
    pass


class Image:

    def __init__(
            self,
            channels: np.ndarray,
            grid: Optional[Grid] = None
    ) -> None:
        try:
            if channels.ndim not in (2, 3):
                raise LatticeFringeImageSpecError(
                    "Channels must be a 2- or 3-dimensional numpy array."
                )
        except AttributeError:
            raise LatticeFringeImageSpecError(
                "Channels must be a 2- or 3-dimensional numpy array."
            )
        if channels.ndim == 2:
            channels = channels[:, :, np.newaxis]
        self.channels = channels
        # infer grid if not provided
        if grid is None:
            x_coords, y_coords = np.meshgrid(
                np.arange(self.height),
                np.arange(self.width)
            )
            grid = Grid(x_coords, y_coords)
        # check grid-channels consistency
        else:
            if self.width != grid.width or self.height != grid.height:
                raise LatticeFringeImageSpecError(
                    "Channel and grid dimensions are not consistent."
                )
        self.grid = grid

    def __getitem__(self, item) -> "Image":
        """
        Image objects can be indexed using numpy array indexing syntax. A
        subset of the Image object will be returned, that is, an Image object
        that encapsulates subsets the channels array and Grid object.

        :param item: The requested item, i.e., an index, slice, mask, etc. All
            valid numpy indexing methods are accepted.
        :return: A subset of the Image object.

        """
        return Image(
            self.channels.__getitem__(item),
            self.grid.__getitem__(item)
        )

    @property
    def width(self) -> int:
        return self.channels.shape[0]

    @property
    def height(self) -> int:
        return self.channels.shape[1]

    @property
    def size(self) -> Tuple[int, int]:
        return self.channels.shape[:-1]

    @property
    def num_channels(self) -> int:
        return self.channels.shape[2]

    @property
    def domain(self) -> Domain:
        return self.grid.domain

    def plot(self) -> None:
        num_channels = self.num_channels
        extent = [*self.grid.x_extent, *self.grid.y_extent]
        # spatial image
        if self.domain == spatial:
            # color image, show as float
            if num_channels == 3:
                pl.imshow(
                    self.channels.astype(float) / self.channels.max(),
                    extent=extent
                )
            # grayscale image, show only channel unscaled
            elif num_channels == 1:
                pl.imshow(self.channels[:, :, 0], extent=extent)
            # multichannel, display average as float
            elif num_channels > 3:
                pl.imshow(
                    self.channels.astype(float).mean(axis=-1),
                    extent=extent
                )
        # frequency image
        else:
            # show log magnitude
            pl.imshow(np.log(np.abs(self.channels[:, :, 0])), extent=extent)
        self.grid.label_axes()

    def resize(
            self,
            scale: Optional[Union[float, Tuple[float]]] = None,
            new_size: Optional[Tuple[int]] = None
    ) -> "Image":
        new_height, new_width = dispatch_resize_args(scale, self.size,
                                                     new_size)
        return Image(
            resize(self.channels, (new_height, new_width), order=1),
            self.grid.resize(new_size=(new_height, new_width))
        )

    def ft(self) -> "Image":
        if self.domain == frequency:
            raise LatticeFringeImageFTError(
                "The Fourier Transform is only meaningful for spatial images."
            )
        if self.num_channels > 1:
            raise LatticeFringeImageFTError(
                "Fourier Transforming is only supported for single-channel "
                "images."
            )
        return Image(
            fftshift(fft2(self.channels[:, :, 0])),
            self.grid.ft()
        )

    def ift(self) -> "Image":
        if self.domain == spatial:
            raise LatticeFringeImageFTError(
                "The image is already spatial domain. Inverse Fourier "
                "transformation is not meaningful."
            )
        if self.num_channels == 1:
            transformed = np.real(ifft2(fftshift(self.channels[:, :, 0])))
        else:
            transformed = np.zeros((self.height, self.width,
                                    self.num_channels))
            for i in range(self.num_channels):
                transformed[:, :, i] = np.real(ifft2(fftshift(
                    self.channels[:, :, i])))
        return Image(transformed, grid=self.grid.ift())

    @staticmethod
    def from_bitmap(
            path: str,
            scale: Optional[float] = 1.0,
            x_scale: Optional[float] = None,
            y_scale: Optional[float] = None,
            unit: str = "pixel",
            x_unit: Optional[str] = None,
            y_unit: Optional[str] = None,
            origin: Optional[Tuple] = None,
            grayscale: bool = True
    ) -> "Image":
        if origin is None:
            origin = (0, 0)
        channels = imread(path)
        shape = channels.shape
        num_dims = channels.ndim
        if num_dims > 3 or num_dims < 2:
            raise LatticeFringeImageIOError(
                "Multi-dimensional images and scalar series are not supported."
                f" The number of dimensions was {num_dims}."
            )
        if num_dims == 2:
            num_channels = 1
        else:
            num_channels = shape[2]
        # convert to grayscale if required
        if grayscale:
            if num_channels == 4:
                channels = rgb2gray(rgba2rgb(channels))[:, :, np.newaxis]
            elif num_channels == 3:
                channels = rgb2gray(channels)[:, :, np.newaxis]
            elif num_channels == 1:
                channels = channels[:, :, np.newaxis]
            else:
                raise LatticeFringeImageIOError(
                    "Image channels must be at most 4-dimensional. The passed "
                    f"channels were {num_channels}-dimensional"
                )
        # convert to grayscale if image channels are same
        # this can occur when reading grayscale images that were saved as color
        if num_channels == 3:
            if all([(c == channels[:, :, 0]).all() for c in channels.T]):
                channels = channels[:, :, 0:1]
        # infer grid
        height = shape[0]
        width = shape[1]
        x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
        x_coords = x_coords - origin[0]
        y_coords = y_coords - origin[1]
        if x_scale is not None:
            x_coords = x_coords * x_scale
        else:
            x_coords = x_coords * scale
        if y_scale is not None:
            y_coords = y_coords * y_scale
        else:
            y_coords = y_coords * scale
        if x_unit is None:
            x_unit = unit
        if y_unit is None:
            y_unit = unit
        return Image(
            channels,
            grid=Grid(
                x_coords,
                y_coords,
                x_unit=x_unit,
                y_unit=y_unit,
                domain=spatial
            )
        )
