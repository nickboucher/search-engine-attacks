# Google Search

This directory contains code for experimenting with search against the Bad Search Wiki as indexed by Google.

## Installation

Install Python requirements:
```sh
pip3 install -r requirements.txt
```

## Usage

Then invoke `./google.py` via the CLI to run the desired commands:
```sh
./google.py --help
```

For example, the visualizations found in the paper can be generated using the pickles included in the `results/` dierctory:
```sh
./google.py graphs hiding results/google_serps_hiding-2022-11-3.pkl
```