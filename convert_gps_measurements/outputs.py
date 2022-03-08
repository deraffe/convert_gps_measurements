"""Output formatters."""

import argparse
import collections
import csv
import logging
from typing import Iterator

from .geometries import Line, Point, Polygon, Shape

log = logging.getLogger(__name__)

output_formats = set()


class OutputFormat:
    """Output Format base class."""

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        output_formats.add(cls)

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.output_path = self.args.output_file

    @property
    def log(self):
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def format(self, shapes: Iterator[Shape]) -> None:
        raise NotImplementedError


class Print(OutputFormat):

    def format(self, shapes: Iterator[Shape]):
        for shape in shapes:
            print(shape)


class Survey2GIS_TSV(OutputFormat):
    SHAPE_CODES = {
        Point: ".",
        Line: "&",
        Polygon: "@",
    }

    def format(self, shapes):
        if not self.output_path.is_dir():
            raise ValueError(
                f"Output path '{self.output_path}' is not a directory."
            )
        object_number_map = collections.defaultdict(lambda: list())
        for shape in shapes:
            meta = shape.points[0].meta
            if "real_object_number" in meta:
                object_number = shape.points[0].meta["real_object_number"]
            else:
                object_number = shape.points[0].meta["object_number"]
            object_number_map[object_number].append(shape)

        for object_number, shape_list in object_number_map.items():
            meta = shape_list[0].points[0].meta
            if "alm_number" in meta:
                output = self.output_path / f"{meta['alm_number']}_{object_number}.tsv"
            else:
                self.log.warn(
                    "No ALM number specified (add 'alm_number' to metadata) for object number %s, continuing without it",
                    object_number
                )
                output = self.output_path / f"{object_number}.tsv"
            self.log.info(f"Writing {output}...")
            with output.open('w') as csvfile:
                fieldnames = [
                    'id', 'name_plus_type', 'x_name', 'x', 'y_name', 'y',
                    'z_name', 'z'
                ]
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    extrasaction='ignore',
                    dialect='excel-tab'
                )
                for shape in shape_list:
                    num_of_points = len(shape.points)
                    for i, point in enumerate(shape.points):
                        point_dict = point.dict()
                        point_dict.update(point_dict["meta"])
                        point_dict.update({
                            "x_name": "X",
                            "y_name": "Y",
                            "z_name": "Z",
                        })
                        del point_dict["meta"]
                        name = "{planum}_{object_code}_{object_number}".format(
                            **point_dict
                        )
                        type_code = ""
                        if i == (num_of_points - 1):
                            type_code = self.SHAPE_CODES[shape.__class__]
                        point_dict["name_plus_type"] = f"{name}{type_code}"
                        writer.writerow(point_dict)
