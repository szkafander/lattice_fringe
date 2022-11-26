from abc import ABC, abstractmethod

from lattice_fringe.common.domain import Domain

from typing import Collection


class LatticeFringeAxesSpecError(Exception):
    pass


class Axes(ABC):

    def __init__(self, names: Collection[str], units: Collection[str]) -> None:
        n = self._check_args(names, units)
        self.names = names
        self.units = units
        self.n = n

    @abstractmethod
    def transform_to(self, domain: Domain) -> "Axes":
        pass

    @staticmethod
    def _check_args(names: Collection[str], units: Collection[str]) -> int:
        try:
            n_names = len(names)
            n_units = len(units)
        except TypeError as e:
            raise LatticeFringeAxesSpecError(
                "names and units must be same-size Collections. The following"
                f" error was raised: {e}."
            )
        if n_names != n_units:
            raise LatticeFringeAxesSpecError(
                "names and units must be same-size Collections. The passed "
                f"arguments were not same-size. names was size {n_names}, "
                f"units was size {n_units}."
            )
        names_non_str = not all([isinstance(n, str) for n in names])
        units_non_str = not all([isinstance(u, str) for u in units])
        if names_non_str or units_non_str:
            c = " contained non-string elements in "
            raise LatticeFringeAxesSpecError(
                "names and units must contain strings. "
                f"{'names' + c + str(names) + '. ' if names_non_str else ''}"
                f"{'units' + c + str(units) + '.' if units_non_str else ''}"
            )
        return n_names


pixel_axes = Axes(["x", "y"], ["pixel", "pixel"])
pixel_frequency_axes = Axes(
    ["x frequency", "y frequency"],
    ["1/pixel", "1/pixel"]
)
