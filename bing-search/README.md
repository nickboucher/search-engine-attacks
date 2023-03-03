# Bing Search

This directory contains code for experimenting with search against the Bad Search Wiki as indexed by Bing.

## Installation

Install Python requirements:
```sh
pip3 install -r requirements.txt
```

## Usage

Then invoke `./bing.py` via the CLI to run the desired commands:
```sh
./bing.py --help
```

For example, the visualizations found in the paper can be generated using the pickles included in the `results/` dierctory:
```sh
./bing.py graphs hiding -s results/bing-srcf_serps_hiding-2022-12-12.pkl -m results/bing-ml_serps_hiding-2022-12-12.pkl
./bing.py graphs surfacing -s results/bing-srcf_serps_surfacing-2022-12-13.pkl -m results/bing-ml_serps_surfacing-2022-12-13.pkl
```