"""Convert GPS measurements to various output formats while filtering the data."""
import argparse
import itertools
import json
import logging
import pathlib

from .filters import filters
from .inputs import input_formats
from .outputs import output_formats

META_JSON_DEFAULT = "meta.json"

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


def configure_meta(args):
    """Configure metadata interactively."""
    data_attrs = {
        "project_name": "project name",
        "alm_number": "ALM number",
    }
    data = None
    try:
        with args.metadata_json.open() as fd:
            data = json.load(fd)
    except (EOFError, FileNotFoundError):
        pass
    if data is None:
        data = {}
    for key, name in data_attrs.items():
        default_value = data.get(key, '')
        value = input(f"Please input {name} [default: {default_value}]: ")
        if value != "":
            data[key] = value
        else:
            data[key] = default_value
    with args.metadata_json.open("w") as fd:
        json.dump(data, fd)


def convert(args):
    """Convert one file format to another."""
    parser = input_format_map[args.input_format](args)
    formatter = output_format_map[args.output_format](args)
    filter_chain = map(lambda name: filters_map[name](args), args.filter)
    shapes = []
    for input_file in args.input_files:
        shapes.append(parser.process_file(input_file))
    data_stream = itertools.chain.from_iterable(shapes)
    for filter_instance in filter_chain:
        data_stream = filter_instance.filter(data_stream)
    formatter.format(data_stream)


def main():
    """Handle arguments and call routines."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel", default="INFO", help="Loglevel", action="store"
    )
    subparsers = parser.add_subparsers(title="Commands")

    plistformats = subparsers.add_parser(
        "list-formats", aliases=["l", "list"], help=list_formats.__doc__
    )
    plistformats.set_defaults(func=list_formats)

    pconfiguremeta = subparsers.add_parser(
        "configure-meta",
        aliases=["configure", "meta"],
        help=configure_meta.__doc__
    )
    pconfiguremeta.set_defaults(func=configure_meta)
    pconfiguremeta.add_argument(
        "--metadata_json",
        type=pathlib.Path,
        default=pathlib.Path(META_JSON_DEFAULT),
        help="Metadata JSON file. Metadata will be written to it."
    )

    pconvert = subparsers.add_parser(
        "convert", aliases=["c"], help=convert.__doc__
    )
    pconvert.set_defaults(func=convert)
    pconvert.add_argument(
        "input_files", nargs="+", type=pathlib.Path, help="Input file(s)"
    )
    pconvert.add_argument("output_file", type=pathlib.Path, help="Output file")
    pconvert.add_argument(
        "--input-format",
        "-i",
        choices=input_format_map.keys(),
        metavar="FORMAT",
        default="Csv",
        help="Input format"
    )
    pconvert.add_argument(
        "--filter",
        "-f",
        nargs="+",
        choices=filters_map.keys(),
        metavar="FILTER",
        default=("Metadata", ),
        help="Filter"
    )
    pconvert.add_argument(
        "--output-format",
        "-o",
        choices=output_format_map.keys(),
        metavar='FORMAT',
        default="Print",
        help="Output format"
    )
    pconvert.add_argument(
        "--metadata-json",
        type=pathlib.Path,
        default=pathlib.Path(META_JSON_DEFAULT),
        help=
        "Metadata JSON file. Will be added as metadata to individual points."
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
