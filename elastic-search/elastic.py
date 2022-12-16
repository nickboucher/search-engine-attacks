#!/usr/bin/env python3
#
# elastic.py
# December 2022
#
# Command-line utility for running adversarial search engine
# indexing experiments using Unicode.
#
import argparse
from indexing import index
from searching import search
from experimenting import experiment
from graphing import graphs
from elasticsearch import Elasticsearch

def main():
    # Main Parser
    parser = argparse.ArgumentParser(description='Adversarial Search Experiments using Elastisearch.')
    parser.add_argument('--host', help='Elasticsearch host', default='localhost')
    parser.add_argument('--port', help='Elasticsearch port', default=9200)
    parser.add_argument('--scheme', help='Elasticsearch scheme', default='http')
    subparsers = parser.add_subparsers(help='Select a command', dest='command', metavar='command', required=True)
    
    #Index Parser
    subparsers.add_parser('index', help='Index Simple Wikipedia Archive', description='Index Simple Wikipedia Archive')
    
    # Search Parser
    search_parser = subparsers.add_parser('search', help='Search Simple Wikipedia Index', description='Search Simple Wikipedia Index')
    search_parser.add_argument('query', help='Query with which to search the index.')

    # Experiment Parser
    experiment_parser = subparsers.add_parser('experiment', help='Run Elasticsearch Experiments', description='Run Elasticsearch Experiments')
    experiment_parser.add_argument('experiment_name', help='Experiment to run. Either "hiding", "surfacing", or "all".')

    # Graphs Parser
    graphs_parser = subparsers.add_parser('graphs', help='Build Graphs for Experimental Results', description='Build Graphs for Experimental Results')
    graphs_parser.add_argument('experiment_name', help='Experimental Graphs to Build. Either "hiding", "surfacing", or "all".')
    graphs_parser.add_argument('pickle_file', help='Pickle file of experimental results for building graphs.')
    
    # Parse arguments
    args = parser.parse_args()

    # Connect to Elasticsearch
    elastic = Elasticsearch([{'host': args.host, 'port': args.port, 'scheme': args.scheme}], request_timeout=30, max_retries=10, retry_on_timeout=True)
    if not elastic.ping():
        exit('Elasticsearch not running. Please start Elasticsearch and try again.')

    # Invoke function to handle verb
    match args.command:
        case 'index' : index(elastic)
        case 'search': search(elastic, args.query)
        case 'experiment': experiment(elastic, args.experiment_name)
        case 'graphs': graphs(args.experiment_name, args.pickle_file)
        case _ : raise ValueError(f'Unknown verb: {args.command}')

if __name__ == '__main__':
    main()
