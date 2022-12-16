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