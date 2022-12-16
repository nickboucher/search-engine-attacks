#!/usr/bin/env python3
#
# searching.py
# December 2022
#
# Utilities for searching indexed Simple Wikipedia. Should be
# called from the command line using elastic.py.
#

def search(elastic, query):
    results = elastic.search(index='_all', query={
            "multi_match": {
                "query": query, 
                "fields": [ "title", "body" ] 
            }
        }, source=['title'])
    print(results)