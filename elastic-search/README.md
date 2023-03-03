# Elasticsearch

This directory contains code attacking the indexing of local installations of Elasticsearch.

## Installation

Install Elasticsearch via Docker:
```sh
docker pull elasticsearch:8.5.3
```

## Usage

Run Elasticsearch via Docker:
```sh
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" elasticsearch:8.5.3
```

Then invoke `./elastic.py` via the CLI to run the desired commands:
```sh
./elastic.py --help
```

Note that the experimental results described in the paper are too large to place in this repository directly, but are included as a GitHub Release with this repository for download. We package these results as gzipped JSONs instead of pickles for size and loading efficiency.

For example, the visualizations found in the paper can be generated using the unzipped JSON files from the GitHub Release, referenced below as extracted within the `results/` directory:
```sh
./elastic.py graphs hiding results/elastic_serps_hiding-2022-12-14.json  
./elastic.py graphs surfacing results/elastic_serps_surfacing-2022-12-16.json
```