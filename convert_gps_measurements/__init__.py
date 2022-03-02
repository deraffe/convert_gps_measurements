"""Convert GPS measurements to various output formats while filtering the data."""
import argparse
import logging

from .filters import filters
from .inputs import input_formats
from .outputs import output_formats

log = logging.getLogger(__name__)
input_format_map = {cls.__name__: cls for cls in input_formats}
output_format_map = {cls.__name__: cls for cls in output_formats}
filters_map = {cls.__name__: cls for cls in filters}


def list_formats(args):
    """List input, output formats and filters."""
    for name, list in (("INPUT FORMATS", input_format_map.keys()),
                       ("OUTPUT_FORMATS", output_format_map.keys()),
                       ("FILTERS", filters_map.keys())):
        print(name)
        for item in list:
            print("  " + item)


def convert(args):
    """Convert one file format to another."""
    raise NotImplementedError  # FIXME


def main():
    """Handle arguments and call routines."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel", default="WARNING", help="Loglevel", action="store"
    )
    subparsers = parser.add_subparsers(title="Commands")

    plistformats = subparsers.add_parser(
        "list-formats", aliases=["l", "list"], help=list_formats.__doc__
    )
    plistformats.set_defaults(func=list_formats)

    pconvert = subparsers.add_parser(
        "convert", aliases=["c"], help=convert.__doc__
    )
    pconvert.set_defaults(func=convert)
    pconvert.add_argument("input_files", nargs="+", help="Input file(s)")
    pconvert.add_argument(
        "--input-format",
        "-i",
        choices=input_format_map.keys(),
        metavar="FORMAT",
        default=("Csv", ),
        help="Input format"
    )
    pconvert.add_argument(
        "--filter",
        "-f",
        nargs="+",
        choices=filters_map.keys(),
        metavar="FILTER",
        default=("NoOp", ),
        help="Filter"
    )
    pconvert.add_argument(
        "--output-format",
        "-o",
        choices=output_format_map.keys(),
        metavar='FORMAT',
        default=("Print", ),
        help="Output format"
    )

    args = parser.parse_args()

    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError("Invalid log level: {}".format(args.loglevel))
    logging.basicConfig(level=loglevel)

    # call command function
    args.func(args)


if __name__ == "__main__":
    main()