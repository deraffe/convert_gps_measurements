"""Output formatters."""

import logging
import pathlib
from typing import Iterator

from .geometries import Line, MeasurementPoint, Point, Polygon, Shape

log = logging.getLogger(__name__)

output_formats = set()


class OutputFormat:
    """Output Format base class."""

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        output_formats.add(cls)

    @property
    def log(self):
        return logging.getLogger(__class__.__name__)

    def __init__(self, shapes: Iterator[Shape], output_path: pathlib.Path):
        self.shapes = shapes
        self.output_path = output_path

    def format(self) -> Iterator[Shape]:
        raise NotImplementedError


class Print(OutputFormat):

    def format(self):
        for shape in self.shapes:
            print(shape)
