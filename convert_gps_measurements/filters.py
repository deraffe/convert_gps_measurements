"""Data filters."""

import argparse
import json
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

    def __init__(self, args: argparse.Namespace):
        self.args = args

    @property
    def log(self):
        return logging.getLogger(__class__.__name__)

    def filter(self, shapes: Iterator[Shape]) -> Iterator[Shape]:
        raise NotImplementedError


class NoOp(Filter):

    def filter(self, shapes: Iterator[Shape]) -> Iterator[Shape]:
        yield from shapes


class Metadata(Filter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata_json = self.args.metadata_json

    def filter(self, shapes):
        data = None
        if self.metadata_json is not None:
            with self.metadata_json.open() as fd:
                data = json.load(fd)
        if data is not None:
            for shape in shapes:
                for point in shape.points:
                    point.meta.update(data)
                yield shape
        else:
            yield from shapes
