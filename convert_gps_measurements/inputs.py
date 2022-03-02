"""Input format parsers."""

import csv
import logging
import pathlib
import argparse
from typing import Iterator, Type

from .geometries import Line, MeasurementPoint, Point, Polygon, Shape

log = logging.getLogger(__name__)

SHAPE_CODES: dict[str, Type[Shape]] = {
    "@": Polygon,
    "&": Line,
    ".": Point,
}

input_formats = set()


class InputFormat:
    """Input Format base class."""

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        input_formats.add(cls)

    def __init__(self, args: argparse.Namespace):
        self.args = args

    @property
    def log(self):
        return logging.getLogger(__class__.__name__)

    def process_file(self, input_file: pathlib.Path) -> Iterator[Shape]:
        raise NotImplementedError


class GermanExcelCsvDialect(csv.excel):
    delimiter = ";"


class Csv(InputFormat):
    """CSV input format"""

    def process_file(self, input_file: pathlib.Path) -> Iterator[Shape]:
        with input_file.open() as filehandle:
            csv_reader = csv.reader(filehandle, dialect=GermanExcelCsvDialect)
            connected_points = []
            for row in csv_reader:
                id, x, y, z, name = row
                data = {"x": x, "y": y, "z": z, "meta": {"id": id}}
                if name is None or name == '':
                    self.log.warn(
                        "Throwing away line, since we don't know how to handle it: %s",
                        row
                    )
                    continue
                if name[-1] in SHAPE_CODES.keys():
                    # We found the end of a shape definition
                    data["meta"]["name"] = name[:-1]
                    point = MeasurementPoint(**data)
                    connected_points.append(point)
                    shape = SHAPE_CODES[name[-1]](points=connected_points)
                    connected_points = []
                    yield shape
                else:
                    data["meta"]["name"] = name
                    point = MeasurementPoint(**data)
                    connected_points.append(point)
            if len(connected_points) > 0:
                self.log.warn(
                    "Found leftover points: %s", connected_points
                )
