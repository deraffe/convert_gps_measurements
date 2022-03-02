"""
Convert GPS measurements to various output formats while filtering the data.
"""
import argparse
import logging

log = logging.getLogger(__name__)

input_formats = (input_csv, )


def main():
    """Handle arguments and call routines."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel", default="WARNING", help="Loglevel", action="store"
    )
    parser.add_argument("input_files", nargs="+", help="Input file(s)")
    parser.add_argument("--input-format", "-i", help="Input format")
    parser.add_argument("--filter", "-f", nargs="+", help="Filter")
    parser.add_argument("--output-format", "-o", help="Output format")

    args = parser.parse_args()

    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError("Invalid log level: {}".format(args.loglevel))
    logging.basicConfig(level=loglevel)


if __name__ == "__main__":
    main()
