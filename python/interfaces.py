import abc

from typing import Collection


class Filter(abc.ABC):

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

    @abc.abstractmethod
    def apply(self, *args, **kwargs):
        pass

    @staticmethod
    @abc.abstractmethod
    def create():
        pass
