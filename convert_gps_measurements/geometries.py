from typing import Union

import pydantic


class MeasurementPoint(pydantic.BaseModel):
    x: float
    y: float
    z: float
    meta: dict[str, Union[str, int]]


class Shape(pydantic.BaseModel):
    points: list[MeasurementPoint]

    def update_point_meta(self, update: dict):
        for point in self.points:
            point.meta.update(update)


class Polygon(Shape):
    pass


class Line(Shape):
    pass


class Point(Shape):

    @property
    def x(self):
        return self.points[0].x

    @property
    def y(self):
        return self.points[0].y

    @property
    def z(self):
        return self.points[0].z
