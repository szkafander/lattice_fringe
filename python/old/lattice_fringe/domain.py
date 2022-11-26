from abc import ABC, abstractmethod
from lattice_fringe.common.axes import Axes


class Domain(ABC):

    @staticmethod
    @abstractmethod
    def transform_axes_to(axes: Axes, domain: "Domain") -> Axes:
        pass


class Spatial(Domain):

    def __repr__(self):
        return "spatial"

    @staticmethod
    def transform_axes_to(axes: Axes, domain: Domain) -> Axes:
        pass


class Frequency(Domain):

    def __repr__(self):
        return "frequency"

    @staticmethod
    def transform_axes_to(axes: Axes, domain: Domain) -> Axes:
        pass


spatial = Spatial()
frequency = Frequency()
