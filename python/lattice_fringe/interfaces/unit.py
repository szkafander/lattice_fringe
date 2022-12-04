from abc import ABC, abstractmethod

from typing import Any


class Unit(ABC):

    @property
    @abstractmethod
    def base(self) -> "Unit":
        pass

    @property
    @abstractmethod
    def multiplier(self) -> float:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def convert_value(self, value: Any, target_unit: "Unit") -> Any:
        return value * self.multiplier / target_unit.multiplier


class FrequencyUnit(Unit, ABC):

    @abstractmethod
    def transform_unit(self) -> "SpatialUnit":
        pass

    def transform_value(self, frequency_value: Any) -> Any:
        return 1 / frequency_value


class SpatialUnit(Unit, ABC):

    @abstractmethod
    def transform_unit(self) -> "FrequencyUnit":
        pass

    def transform_value(self, spatial_value: Any) -> Any:
        return 1 / spatial_value
