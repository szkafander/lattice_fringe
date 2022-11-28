from abc import ABC, abstractmethod


class Unit(ABC):

    @property
    @abstractmethod
    def base(self, *args, **kwargs) -> "Unit":
        pass

    @property
    @abstractmethod
    def multiplier(self, *args, **kwargs) -> int:
        pass


class FrequencyUnit(Unit, ABC):

    @abstractmethod
    def transform(self, *args, **kwargs) -> "SpatialUnit":
        pass


class SpatialUnit(Unit, ABC):

    @abstractmethod
    def transform(self, *args, **kwargs) -> "FrequencyUnit":
        pass
