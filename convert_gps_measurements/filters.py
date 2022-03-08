"""Data filters."""

import argparse
import collections
import copy
import json
import logging
from typing import Iterator

from .geometries import Polygon, Shape

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
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def filter(self, shapes: Iterator[Shape]) -> Iterator[Shape]:
        raise NotImplementedError


class NoOp(Filter):

    def filter(self, shapes: Iterator[Shape]) -> Iterator[Shape]:
        yield from shapes


class JsonMetadata(Filter):

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
                shape.update_point_meta(data)
                yield shape
        else:
            yield from shapes


class Survey2GIS(Filter):

    def wiggle_points(
        self,
        shape: Shape,
        adjustment: tuple[float, float, float] = (0.001, 0.001, 0.0)
    ) -> Shape:
        x_adj, y_adj, z_adj = adjustment
        for point in shape.points:
            point.x += x_adj
            point.y += y_adj
            point.z += z_adj
        return shape

    def filter(self, shapes):
        object_number_code_map = collections.defaultdict(
            lambda: collections.defaultdict(lambda: list())
        )
        for shape in shapes:
            object_number = shape.points[0].meta["object_number"]
            object_code = shape.points[0].meta["object_code"]
            if object_code in ("PR-A", "PR-B", "FG"):
                self.log.debug(
                    f"Adding {object_code} object {object_number} to map..."
                )
                object_number_code_map[object_number][object_code].append(
                    shape
                )
        for object_number, object_code_map in object_number_code_map.items():
            if not "PR-A" in object_code_map:
                self.log.warn(
                    "No PR-A objects found for object number %s, skipping",
                    object_number
                )
                continue
            else:
                found = False
                for shape in object_code_map["PR-A"]:
                    for point in shape.points:
                        if point.meta.get("object_code", None) == "PR-B":
                            found = True
                            break
                if not found:
                    self.log.warn(
                        "No PR-B objects found for object number %s, skipping",
                        object_number
                    )
            if "FG" in object_code_map:
                shape_list = object_code_map["FG"]
                yield from shape_list
                if len(shape_list) < 5:
                    self.log.warn(
                        "Only %d FG objects for object number %s, should be 5",
                        len(shape_list), object_number
                    )
                first_three_pointshapes = shape_list[:3]
                first_three_points = []
                for pointshape in first_three_pointshapes:
                    first_three_points.append(
                        copy.deepcopy(pointshape.points[0])
                    )
                dummy_polygon = Polygon(points=first_three_points)
                self.wiggle_points(dummy_polygon)
                dummy_polygon.update_point_meta({
                    "object_code": "G",
                    "object_number": "999",
                    "real_object_number": object_number,
                })
                yield dummy_polygon
            else:
                self.log.warn(
                    "No FG objects found for object number %s, skipping",
                    object_number
                )
                continue
            if "PR-A" in object_code_map:
                # PR-B should always be the second point, thus it won't be in the map
                shape_list = object_code_map["PR-A"]
                yield from shape_list
                if len(shape_list) > 1:
                    self.log.warn(
                        "Found multiple PR objects for object number %s - continuing with first",
                        object_number
                    )
                gr_shape = copy.deepcopy(shape_list[0])
                gr_shape.update_point_meta({"object_code": "GR"})
                self.wiggle_points(gr_shape)
                yield gr_shape
            else:
                self.log.warn(
                    "No PR-A object found for object number %s", object_number
                )
