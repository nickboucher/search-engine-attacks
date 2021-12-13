#!/usr/bin/env python3
#
# babel.py
# December 2021
#
# Command-line utility for running adversarial search engine
# indexing experiments using Unicode.
#
import argparse

def index():
    raise NotImplementedError()

def search():
    raise NotImplementedError()

def main():
    parser = argparse.ArgumentParser(description='Adversarial Search Indexing.')
    parser.add_argument('command', help="One of 'index' or 'search'", metavar="<command>")
    args = parser.parse_args()

    match args.command:
        case 'index' : index()
        case 'search' : search()
        case _ : raise ValueError(f'Unknown verb: {args.command}')

if __name__ == '__main__':
    main()
