#!/usr/bin/env python3
#
# experimenting.py
# December 2022
#
# Utilities for searching experimental queries against perturbed
# Simple Wikipedia. Should be called from the command line using elastic.py.
#
import json
from tqdm.auto import tqdm
from datetime import datetime
from os.path import exists
from perturbations import unperturb

def experiment(elastic, experiment_name):
    match experiment_name:
        case 'hiding': hiding_experiment(elastic)
        case 'surfacing': surfacing_experiment(elastic)
        case 'all': hiding_experiment(elastic); surfacing_experiment(elastic)
        case _ : raise ValueError(f'Unknown experiment: {experiment_name}')

def hiding_experiment(elastic):
    # Run Hiding Experiment
    filename = f'elastic_serps_hiding-{datetime.now().strftime("%Y-%m-%d")}.json'
    if exists(filename):
        print('Loading previous results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = json.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = elastic.count(index='_all', query={ "match_all": {} })['count']
    write_interval = count // 20 # Write every 5% of the way through

    for i,doc in tqdm(enumerate(all_docs(elastic, index='_all')), total=count, desc='Hiding Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        # Begin experiment
        technique = doc['_index']
        article = doc['_source']['title']
        title = unperturb(article, technique)

        serp = elastic.search(index=technique, query={
                "multi_match": {
                    "query": title, 
                    "fields": [ "title", "body" ] 
                }
            }, source=['title'])

        serps.append({
            'query': {
                'article': article,
                'technique': technique,
                'title': title
            },
            'result': dict(serp)
        })

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_json(filename, serps)

    # Write final results to file
    write_json(filename, serps)
    print(f'Hiding experiment complete. Results written to {filename}.')


def surfacing_experiment(elastic):
    # Run Showing Experiment
    filename = f'elastic_serps_surfacing-{datetime.now().strftime("%Y-%m-%d")}.json'
    if exists(filename):
        print('Loading previous results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = json.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    serps = []
    filename = f'elastic_serps_surfacing-2-{datetime.now().strftime("%Y-%m-%d")}.json'
    count = elastic.count(index='_all', query={ "match_all": {} })['count']
    write_interval = count // 20 # Write every 5% of the way through

    for i,doc in tqdm(enumerate(all_docs(elastic, index='_all')), total=count, desc='Surfacing Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        # Begin experiment
        technique = doc['_index']
        article = doc['_source']['title']
        title = unperturb(article, technique)

        serp = elastic.search(index='_all', query={
                "multi_match": {
                    "query": article, 
                    "fields": [ "title", "body" ] 
                }
            }, source=['title'])

        serps.append({
            'query': {
                'article': article,
                'technique': technique,
                'title': title
            },
            'result': dict(serp)
        })

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_json(filename, serps)

    # Write final results to file
    write_json(filename, serps)
    print(f'Surfacing experiment complete. Results written to {filename}.')

def all_docs(elastic, index, pagesize=1000, scroll_timeout="30m", **kwargs):
    """
    Helper to iterate ALL values from a single index
    Yields all the documents.
    """
    is_first = True
    while True:
        # Scroll next
        if is_first: # Initialize scroll
            result = elastic.search(index=index, scroll=scroll_timeout, **kwargs, body={
                "size": pagesize,
                "sort": ["_doc"] # Elasticsearch optimization
            }, source=['title'])
            is_first = False
        else:
            result = elastic.scroll(body={
                "scroll_id": scroll_id,
                "scroll": scroll_timeout
            })
        scroll_id = result["_scroll_id"]
        hits = result["hits"]["hits"]
        # Stop after no more docs
        if not hits:
            break
        # Yield each entry
        yield from (hit for hit in hits)

def write_json(filename, serps):
    with open(filename, 'wb') as f:
        json.dump({
            'serps': serps
        }, f)