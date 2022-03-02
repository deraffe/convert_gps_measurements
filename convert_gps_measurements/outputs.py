"""Output formatters."""

import logging
import pathlib
import argparse
from typing import Iterator

from .geometries import Shape

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
        return logging.getLogger(__class__.__name__)


    def format(self) -> Iterator[Shape]:
        raise NotImplementedError


class Print(OutputFormat):

    def format(self, shapes: Iterator[Shape]):
        for shape in shapes:
            print(shape)
