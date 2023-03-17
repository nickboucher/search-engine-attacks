#!/usr/bin/env python3
#
# graphing.py
# December 2022
#
# Utilities for building graphs of experimental results.
# Should be called from the command line using elastic.py.
#
import json
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from collections import Counter
from perturbations import perturbations, unperturb

def graphs(experiment_name, json_file):
    match experiment_name:
        case 'hiding': hiding_graphs(json_file)
        case 'surfacing': surfacing_graphs(json_file)
        case 'all': hiding_graphs(json_file); surfacing_graphs(json_file)
        case _ : raise ValueError(f'Unknown experiment: {experiment_name}')

def hiding_graphs(json_file):
    # Load the pickle file
    print('Loading JSON file...')
    with open(json_file, 'rb') as f:
        serps = json.load(f)['serps']
    
    performance = {}
    for technique in perturbations:
        performance[technique] = { 'success': 0, 'total': 0 }
    for serp in tqdm(serps, desc='Processing SERPs'):
        technique = serp['query']['technique']
        performance[technique]['total'] += 1
        for page in serp['result']['hits']['hits']:
            if unperturb(page['_source']['title'],page['_index']) == serp['query']['article']:
                performance[technique]['success'] += 1

    values = list(zip(performance.keys(),
                    map(lambda x: x['success'], performance.values()),
                    map(lambda x: x['total'] - x['success'], performance.values())))
    values.sort(key=lambda x: -x[1]-x[2])
    x,y1,y2 = tuple(zip(*values))

    plt.style.use('ggplot')
    _, ax = plt.subplots()
    top_bars = ax.bar(x, y1, label='Perturbed Target Present in SERP', color='tomato', bottom=y2)
    bottom_bars = ax.bar(x, y2, label='Perturbed Target Absent in SERP', color='lightseagreen')
    ax.set_ylim([0,249000])
    ax.legend(loc='lower center', bbox_to_anchor=(.5,-.31))
    ax.set_title('Elasticsearch:\nPerturbed Index & Unperturbed Queries', fontsize=16, y=1.06)
    ax.set_xlabel('Perturbation Technique')
    ax.set_ylabel('Number of Indexed Pages')
    for top_bar, bottom_bar in zip(top_bars, bottom_bars):
        top, bottom = top_bar.get_height(), bottom_bar.get_height()
        ax.annotate('$M_h$='+f'{bottom/(top+bottom):0.2f}'.lstrip('0').replace('1.00','1').replace('.00','0'),
                    xy=(top_bar.get_x() + top_bar.get_width() / 2, top+bottom),
                    xytext=(0, 3), # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.savefig('elastic_hiding.svg', bbox_inches='tight')
    plt.savefig('elastic_hiding.png', bbox_inches='tight')
    print('Hiding bar chart saved to elastic_hiding.[svg/png].')

def surfacing_graphs(json_file):
    # Load the pickle file
    print('Loading JSON file...')
    with open(json_file, 'rb') as f:
        serps = json.load(f)['serps']

    count = Counter()
    for serp in tqdm(serps, desc='Processing SERPs'):
        hit = 'miss'
        o_perturbation = serp['query']['technique']
        o_title = serp['query']['title']
        for page in serp['result']['hits']['hits']:
            if page['_source']['title'] == o_title:
                hit = 'hit'
                break
        count[f'{o_perturbation}-{hit}'] += 1

    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 5)
    for idx, technique in enumerate(perturbations):
        pct = count[f'{technique}-hit']/max(count[f'{technique}-hit']+count[f'{technique}-miss'],1)
        axs[idx//5,idx%5].pie([pct,1-pct], autopct='%1.0f%%', colors=['lightsteelblue', 'lightcoral'])
        axs[idx//5,idx%5].set_title(technique)
        axs[idx//5,idx%5].text(0,-1.4, '$M_s$='+(f'{pct:.2f}'.lstrip('0').replace('1.00','1').replace('.00','0')), size=8, ha='center')
    plt.legend(['Perturbed Target Present in SERP','Perturbed Target Absent in SERP'], loc='lower center', bbox_to_anchor=(-1.9,-1.45))
    fig.suptitle("Elasticsearch:\nPerturbed Result from Perturbed Query", fontsize=16, y=1.05)

    plt.savefig('elastic_surfacing.svg', bbox_inches='tight')
    plt.savefig('elastic_surfacing.png', bbox_inches='tight')
    print('Surfacing pie charts saved to elastic_surfacing.[svg/png].')