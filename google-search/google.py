#!/usr/bin/env python3
#
# google.py
# February 2023
#
# Command-line utility for running adversarial search engine
# indexing experiments using Unicode.
#
import argparse
from experimenting import experiment
from graphing import graphs

def main():
    # Main Parser
    parser = argparse.ArgumentParser(description='Adversarial Search Experiments using Google.')
    subparsers = parser.add_subparsers(help='Select a command', dest='command', metavar='command', required=True)

    # Experiment Parser
    experiment_parser = subparsers.add_parser('experiment', help='Run Google Experiments', description='Run Google Experiments')
    experiment_parser.add_argument('experiment_name', help='Experiment to run. Either "hiding", "surfacing", or "all".')
    # Note: Table should be downloaded using Google Account and extracted
    # https://search.google.com/search-console/index/drilldown?resource_id=https%3A%2F%2Fbadsearch.soc.srcf.net%2F&pages=ALL_URLS&sharing_key=lC6RrfPkKJ1LTJcGMRvFyw
    # Go to: Export -> Download CSV
    # This page may be inaccessible to later users. If so, please create a new Programmable Search engine, update the IDs in experimenting.py, and export the new table after indexing.
    experiment_parser.add_argument('table', help='CSV of indexed pages exported from Google Search Console.')
    experiment_parser.add_argument('key_file', help='File containing Google API key.')

    # Graphs Parser
    graphs_parser = subparsers.add_parser('graphs', help='Build Graphs for Experimental Results', description='Build Graphs for Experimental Results')
    graphs_parser.add_argument('experiment_name', help='Experimental Graphs to Build. Either "hiding", "surfacing", or "all".')
    graphs_parser.add_argument('pickle_file', help='Pickle file of experimental results for building graphs.')
    
    # Parse arguments
    args = parser.parse_args()

    # Invoke function to handle verb
    match args.command:
        case 'experiment': experiment(args.table, args.key_file, args.experiment_name)
        case 'graphs': graphs(args.experiment_name, args.pickle_file)
        case _ : raise ValueError(f'Unknown verb: {args.command}')

if __name__ == '__main__':
    main()
