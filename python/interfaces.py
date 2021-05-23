import abc

from typing import Collection


class Filter(abc.ABC):

    @property
    @abc.abstractmethod
    def coordinate(self):
        pass

    @abc.abstractmethod
    def apply(self, *args, **kwargs):
        pass


class FilterBank(abc.ABC):

    def __init__(
            self,
            filters: Collection[Filter],
            abscissae: Collection
    ) -> None:
        self.filters = filters
        self.abscissae = abscissae

    @property
    def num_filters(self):
        return len(self.filters)

    @property
    def coordinates(self):
        return [f.coordinate for f in self.filters]

    @abc.abstractmethod
    def apply(self, *args, **kwargs):
        pass

    @staticmethod
    @abc.abstractmethod
    def create():
        pass
