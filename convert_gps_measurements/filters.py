"""Data filters."""

import logging
from typing import Iterator

from .geometries import Shape

log = logging.getLogger(__name__)

filters = set()


class Filter:
    """Filter base class."""

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        filters.add(cls)

    @property
    def log(self):
        return logging.getLogger(__class__.__name__)

    def filter(self, shapes: Iterator[Shape]) -> Iterator[Shape]:
        raise NotImplementedError


class NoOp(Filter):

    def filter(self, shapes: Iterator[Shape]) -> Iterator[Shape]:
        yield from shapes
