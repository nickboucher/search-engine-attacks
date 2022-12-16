#!/usr/bin/env python3
#
# graphing.py
# December 2022
#
# Utilities for building graphs of experimental results.
# Should be called from the command line using elastic.py.
#
import pickle
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from collections import Counter
from perturbations import perturbations, unperturb

def graphs(experiment_name, pickle_file):
    match experiment_name:
        case 'hiding': hiding_graphs(pickle_file)
        case 'surfacing': surfacing_graphs(pickle_file)
        case 'all': hiding_graphs(pickle_file); surfacing_graphs(pickle_file)
        case _ : raise ValueError(f'Unknown experiment: {experiment_name}')

def hiding_graphs(pickle_file):
    # Load the pickle file
    with open(pickle_file, 'rb') as f:
        serps = pickle.load(f)['serps']

    ## Percentage Graph
    performance = {}
    for technique in perturbations:
        performance[technique] = { 'success': 0, 'total': 0 }

    for serp in serps:
        technique = serp['query']['technique']
        performance[technique]['total'] += 1
        for page in serp['result']['hits']['hits']:
            if unperturb(page['_source']['title'],page['_index']) == serp['query']['article']:
                performance[technique]['success'] += 1

    values = list(zip(performance.keys(), map(lambda x: x['success']/x['total'], performance.values())))
    values.sort(key=lambda x: -x[1])
    x,y = tuple(zip(*values))

    plt.style.use('ggplot')
    plt.bar(x, y, color=['blue', 'green', 'orange', 'red'])
    plt.xlabel('Perturbation Technique')
    plt.ylabel('Perturbed Target in SERP')
    plt.title('Elasticsearch Performance\nagainst Perturbed Content')
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

    plt.savefig('elastic_perturbed_index.svg')
    plt.savefig('elastic_perturbed_index.png')
    print('Percentage graph saved to elastic_perturbed_index.[svg/png].')

    ## Absolute Graph
    values = list(zip(performance.keys(),
                    map(lambda x: x['success'], performance.values()),
                    map(lambda x: x['total'] - x['success'], performance.values())))
    values.sort(key=lambda x: -x[1]-x[2])
    x,y1,y2 = tuple(zip(*values))

    plt.style.use('ggplot')
    _, ax = plt.subplots()
    ax.bar(x, y1, label='Discoverable', color='green', bottom=y2)
    ax.bar(x, y2, label='Undiscoverable', color='red')
    ax.legend()
    ax.set_title('Elasticsearch Performance\nagainst Perturbed Content')
    ax.set_xlabel('Perturbation Technique')
    ax.set_ylabel('Number of Indexed Pages')

    plt.savefig('elastic_perturbed_index_absolute.svg')
    plt.savefig('elastic_perturbed_index_absolute.png')
    print('Absolute graph saved to elastic_perturbed_index_absolute.[svg/png].')

def surfacing_graphs(pickle_file):
    # Load the pickle file
    with open(pickle_file, 'rb') as f:
        serps = pickle.load(f)['serps']

    # Bar Graphs
    hitCount = Counter()
    missCount = Counter()
    for serp in serps:
        results = serp['result']['hits']['total']['value']
        count = str(results)
        if results >= 10:
            count = '10+'
        hit = False
        if results > 0:
            article = serp['query']['article']
            for page in serp['result']['hits']['hits']:
                if page['_source']['title'] == article:
                    hit = True
                    break
        if hit:
            hitCount[count] += 1
            missCount[count] += 0
        else:
            hitCount[count] += 0
            missCount[count] += 1


    x,y1 = tuple(zip(*sorted(hitCount.items(), key=lambda x: int(x[0][:2]))))

    x2,y2 = tuple(zip(*sorted(missCount.items(), key=lambda x: int(x[0][:2]))))

    assert(x==x2)

    plt.style.use('ggplot')
    _, ax = plt.subplots()
    ax.bar(x, y1, label='Target Present', color='lightseagreen')
    ax.bar(x, y2, label='Target Absent', color='tomato', bottom=y1)
    ax.legend()
    ax.set_xlabel('Number of Search Results')
    ax.set_ylabel('Occurrences')
    ax.set_title('Elasticsearch Search\nUsing Perturbed Content')

    plt.savefig('elastic_perturbed_surfacing.svg')
    plt.savefig('elastic_perturbed_surfacing.png')
    print('Surfacing bar chart saved to elastic_perturbed_surfacing.[svg/png].')

    # Pie Charts
    count = Counter()
    for serp in serps:
        hit = 'miss'
        o_perturbation = serp['query']['technique']
        o_title = serp['query']['title']
        for page in serp['result']['hits']['hits']:
            if page['_source']['title'] == o_title:
                hit = 'hit'
                break
        count[f'{o_perturbation}-{hit}'] += 1

    fig, axs = plt.subplots(2, 5)

    for idx, technique in enumerate(perturbations):
        pct = count[f'{technique}-hit']/max(count[f'{technique}-hit']+count[f'{technique}-miss'],1)
        axs[idx//5,idx%5].pie([pct,1-pct], labels=['Present', 'Absent'], autopct='%1.0f%%', colors=['lightseagreen', 'tomato'])
        axs[idx//5,idx%5].set_title(technique)

    fig.suptitle("Percentage Target Page in Elasticsearch SERP per Technique", fontsize=16)

    plt.savefig('elastic_perturbed_surfacing_techniques.svg')
    plt.savefig('elastic_perturbed_surfacing_techniques.png')
    print('Surfacing pie charts saved to elastic_perturbed_surfacing_techniques.[svg/png].')