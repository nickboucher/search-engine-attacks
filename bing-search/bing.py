#!/usr/bin/env python3
#
# bing.py
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
    parser = argparse.ArgumentParser(description='Adversarial Search Experiments using Bing.')
    subparsers = parser.add_subparsers(help='Select a command', dest='command', metavar='command', required=True)

    # Experiment Parser
    experiment_parser = subparsers.add_parser('experiment', help='Run Bing Experiments', description='Run Bing Experiments')
    experiment_parser.add_argument('experiment_name', help='Experiment to run. Either "hiding", "surfacing", or "all".')
    experiment_parser.add_argument('key_file', help='File containing Google API key.')
    experiment_parser.add_argument('site', help='Instance of Bad Search Wiki to Target. Either "srcf", "ml", or "all".')

    # Graphs Parser
    graphs_parser = subparsers.add_parser('graphs', help='Build Graphs for Experimental Results', description='Build Graphs for Experimental Results')
    graphs_parser.add_argument('experiment_name', help='Experimental Graphs to Build. Either "hiding", "surfacing", or "all".')
    graphs_parser.add_argument('-s', '--srcf_pickle_file', help='Pickle file of experimental SRCF domain results for building graphs.')
    graphs_parser.add_argument('-m', '--ml_pickle_file', help='Pickle file of experimental ML domain results for building graphs.')

    # Parse arguments
    args = parser.parse_args()

    # Invoke function to handle verb
    match args.command:
        case 'experiment': experiment(args.site, args.key_file, args.experiment_name)
        case 'graphs': graphs(args.experiment_name, args.srcf_pickle_file, args.ml_pickle_file)
        case _ : raise ValueError(f'Unknown verb: {args.command}')

if __name__ == '__main__':
    main()