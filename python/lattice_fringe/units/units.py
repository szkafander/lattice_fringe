# conversion: cm -> km (unit conv.)
# transformation: cm -> 1/cm (FT)

from lattice_fringe.interfaces.unit import Unit, SpatialUnit, FrequencyUnit

from typing import Any


class Meter(SpatialUnit):

    def __repr__(self) -> str:
        return "m"

    @property
    def base(self) -> Unit:
        return Meter()

    @property
    def multiplier(self) -> float:
        return 1

    def transform_unit(self) -> FrequencyUnit:
        return InverseMeter()


class InverseMeter(FrequencyUnit):

    def __repr__(self) -> str:
        return "1/m"

    @property
    def base(self) -> Unit:
        return InverseMeter()

    @property
    def multiplier(self) -> float:
        return 1

    def transform_unit(self) -> SpatialUnit:
        return Meter()


class NanoMeter(SpatialUnit):

    def __repr__(self) -> str:
        return "nm"

    @property
    def base(self) -> Unit:
        return Meter()

    @property
    def multiplier(self) -> float:
        return 1e-9

    def transform_unit(self) -> FrequencyUnit:
        return InverseNanoMeter()


class InverseNanoMeter(FrequencyUnit):

    def __repr__(self) -> str:
        return "1/nm"

    @property
    def base(self) -> Unit:
        return InverseMeter()

    @property
    def multiplier(self) -> float:
        return 1e9

    def transform_unit(self) -> SpatialUnit:
        return NanoMeter()
