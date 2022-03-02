# Convert GPS Measurements

This program is supposed to convert between CSV input files and SHP output files, but can easily be extended to any number of formats.


## Installation

You need [Python](https://www.python.org/) and [Poetry](https://python-poetry.org/docs/).

Using poetry, you should be able to install all necessary dependencies:
```
poetry install
```

## Usage

```
% ./convert.py convert --help
usage: convert.py convert [-h] [--input-format FORMAT] [--filter FILTER [FILTER ...]] [--output-format FORMAT] [--metadata-json METADATA_JSON] input_files [input_files ...] output_file

positional arguments:
  input_files           Input file(s)
  output_file           Output file

options:
  -h, --help            show this help message and exit
  --input-format FORMAT, -i FORMAT
                        Input format
  --filter FILTER [FILTER ...], -f FILTER [FILTER ...]
                        Filter
  --output-format FORMAT, -o FORMAT
                        Output format
  --metadata-json METADATA_JSON
                        Metadata JSON file. Will be added as metadata to individual points.
```
