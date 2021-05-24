import matplotlib.pyplot as pl
import matplotlib.axes as ax
import numpy as np
import utils
import warnings

from imageio import imread
from scipy.fft import fft2
from skimage.color import rgb2gray, rgba2rgb
from skimage.transform import resize

from typing import Optional, Tuple, Union


class Domain:
    pass


class Spatial(Domain):
    pass


class Frequency(Domain):
    pass


spatial = Spatial()
frequency = Frequency()


def _dispatch_resize_args(scale, old_size, new_size):
    if float is None and new_size is None:
        raise ValueError("At least one of 'scale' and 'new_size' must be "
                         "specified.")
    if isinstance(scale, float):
        scale = [scale, scale]
    if new_size is None:
        new_height = np.round(old_size[0] * scale).astype(int)
        new_width = np.round(old_size[1] * scale).astype(int)
    else:
        new_height = new_size[0]
        new_width = new_size[1]
    return new_height, new_width


class Cache:

    def __init__(
            self,
            *attributes: str
    ) -> None:
        for attribute in attributes:
            setattr(self, attribute, None)


class Grid:

    def __init__(
            self,
            x_coords: np.ndarray,
            y_coords: np.ndarray,
            x_name: str = "x",
            y_name: str = "y",
            x_unit: str = "pixel",
            y_unit: str = "pixel",
            domain: Domain = spatial
    ) -> None:
        if x_coords.ndim not in [1, 2] or y_coords.ndim not in [1, 2]:
            raise ValueError("x_coords and y_coords must be 1- or "
                             "2-dimensional arrays.")
        if x_coords.ndim == 1 and y_coords.ndim == 1:
            x_coords, y_coords = np.meshgrid(x_coords, y_coords)
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.x_name = x_name
        self.y_name = y_name
        self.x_unit = x_unit
        self.y_unit = y_unit
        self.domain = domain

    def __eq__(self, other: "Grid") -> bool:
        if not isinstance(other, Grid):
            raise ValueError("Grids can only be compared to Grids.")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            try:
                x_equal = (self.x_coords == other.x_coords).all()
            except Exception:
                return False
            try:
                y_equal = (self.y_coords == other.y_coords).all()
            except Exception:
                return False
        return self.domain == other.domain and x_equal and y_equal

    def __getitem__(self, item) -> "Grid":
        """
        Grid objects can be indexed using numpy array indexing syntax.
        N-dimensional slices will be converted to 2-dimensional slices.

        :param item: The requested item, i.e., an index, slice, mask, etc. All
            valid numpy indexing methods are accepted.
        :return: A subset of the Grid object.
        """
        # make the slice 2-dimensional if needed
        if len(item) > 2:
            item = item[:-1]
        return Grid(
            self.x_coords.__getitem__(item),
            self.y_coords.__getitem__(item),
            x_name=self.x_name,
            y_name=self.y_name,
            x_unit=self.x_unit,
            y_unit=self.y_unit,
            domain=self.domain
        )

    @property
    def x_axis(self) -> np.ndarray:
        return self.x_coords[0, :]

    @property
    def y_axis(self) -> np.ndarray:
        return self.y_coords[:, 0]

    @property
    def x_extent(self) -> np.ndarray:
        return self.x_axis[[0, -1]]

    @property
    def y_extent(self) -> np.ndarray:
        return self.y_axis[[0, -1]]

    @property
    def width(self) -> int:
        return len(self.x_axis)

    @property
    def height(self) -> int:
        return len(self.y_axis)

    @property
    def size(self) -> Tuple[float, float]:
        return self.height, self.width

    @property
    def x_delta(self) -> float:
        return self.x_axis[1] - self.x_axis[0]

    @property
    def y_delta(self) -> float:
        return self.y_axis[1] - self.y_axis[0]

    def ft(self) -> "Grid":
        if self.domain == frequency:
            raise ValueError("This grid is already frequency-domain. Fourier "
                             "Transforming is not meaningful.")
        n_x = self.width
        n_y = self.height
        return Grid(
            np.arange(-n_x / 2, n_x / 2) / self.x_delta / n_x,
            np.arange(-n_y / 2, n_y / 2) / self.y_delta / n_y,
            x_name=f"{self.x_name} frequency",
            y_name=f"{self.y_name} frequency",
            x_unit=f"1/{self.x_unit}",
            y_unit=f"1/{self.y_unit}",
            domain=frequency
        )

    def ift(self) -> "Grid":
        xr = self.x_extent[1] - self.x_extent[0]
        yr = self.y_extent[1] - self.y_extent[0]
        x_name = self.x_name
        y_name = self.y_name
        x_unit = self.x_unit
        y_unit = self.y_unit
        if x_name[-10:] == " frequency":
            x_name = x_name[1:]
        if y_name[-10:] == " frequency":
            y_name = y_name[1:]
        if x_unit[:2] == "1/":
            x_unit = x_unit[2:]
        if y_unit[:2] == "1/":
            y_unit = y_unit[2:]
        return Grid(
            np.linspace(0, xr, len(self.x_axis)),
            np.linspace(0, yr, len(self.y_axis)),
            x_name=x_name,
            y_name=y_name,
            x_unit=x_unit,
            y_unit=y_unit
        )

    def resize(
            self,
            scale: Optional[Union[float, Tuple[float]]] = None,
            new_size: Optional[Tuple[int, int]] = None
    ) -> "Grid":
        n_x, n_y = _dispatch_resize_args(scale, self.size, new_size)
        x_axis = np.linspace(self.x_extent[0], self.x_extent[1], n_x)
        y_axis = np.linspace(self.y_extent[0], self.y_extent[1], n_y)
        return Grid(
            x_axis,
            y_axis,
            x_unit=self.x_unit,
            y_unit=self.y_unit,
            domain=self.domain
        )

    def label_axes(self, axes: Optional[ax.Axes] = None) -> None:
        axes = axes or pl.gca()
        axes.set_xlabel(
            self.x_name + f", {self.x_unit}" if self.x_unit else "")
        axes.set_ylabel(
            self.y_name + f", {self.y_unit}" if self.y_unit else "")

    def show(self) -> None:
        xx = self.x_coords / np.abs(self.x_coords).max()
        yy = self.y_coords / np.abs(self.y_coords).max()
        c = xx
        m = -xx
        y = yy
        pl.imshow(
            utils.overlay(c, m, y),
            extent=(*self.x_extent, *self.y_extent)
        )
        self.label_axes()


class Image:

    def __init__(
            self,
            channels: np.ndarray,
            grid: Optional[Grid] = None
    ) -> None:
        try:
            if channels.ndim not in (2, 3):
                raise ValueError("Channels must be a 2- or 3-dimensional numpy"
                                 "array.")
        except AttributeError:
            raise ValueError("Channels must be a 2- or 3-dimensional numpy "
                             "array.")
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
                raise ValueError("Channel and grid dimensions are not "
                                 "consistent.")
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
    def num_channels(self) -> int:
        return self.channels.shape[2]

    @property
    def domain(self) -> Domain:
        return self.grid.domain

    def show(self) -> None:
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
        new_height, new_width = _dispatch_resize_args(scale, new_size)
        return Image(
            resize(self.channels, (new_height, new_width), order=1),
            self.grid.resize(new_size=(new_height, new_width))
        )

    def ft(self) -> "Image":
        if self.domain == frequency:
            raise ValueError("The Fourier Transform is only meaningful for "
                             "spatial images.")
        if self.num_channels > 1:
            raise ValueError("Fourier Transforming is only supported for "
                             "single-channel images.")
        return Image(
            fft2(self.channels[:, :, 0]),
            self.grid.ft()
        )

    def ift(self) -> "Image":
        pass

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
            raise ValueError(f"Multi-dimensional images and scalar series "
                             f"are not supported. The number of dimensions "
                             f"was {num_dims}.")
        if num_dims == 2:
            num_channels = 1
        else:
            num_channels = shape[2]
        # convert to grayscale if required
        if grayscale:
            if num_channels == 4:
                channels = rgb2gray(rgba2rgb(channels))[:, :, np.newaxis]
            else:
                channels = rgb2gray(channels)[:, :, np.newaxis]
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


im = Image.from_bitmap("D:\\projects\\oneauthor-review\\image.png")
