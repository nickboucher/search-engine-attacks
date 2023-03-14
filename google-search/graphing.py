#!/usr/bin/env python3
#
# graphing.py
# February 2023
#
# Utilities for building graphs of experimental results.
# Should be called from the command line using elastic.py.
#
import pickle
import matplotlib.pyplot as plt
from collections import Counter
from perturbations import perturbations

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

    performance = {}
    for technique in ['base', 'zwsp', 'zwnj', 'zwj', 'rlo', 'bksp', 'del', 'homo']:
        performance[technique] = { 'success': 0, 'total': 0 }

    for serp in serps:
        technique = serp['query']['technique']
        performance[technique]['total'] += 1
        if int(serp['result']['searchInformation']['totalResults']) > 0:
            for page in serp['result']['items']:
                url = page['link'].split('/')
                if len(url) == 5:
                    if int(url[-1].split('.')[0]) == serp['query']['article']:
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
    ax.set_ylim([0,110])
    ax.legend(loc='lower center', bbox_to_anchor=(.5,-.31))
    ax.set_title('Google:\nPerturbed Index & Unperturbed Queries', fontsize=16, y=1.06)
    ax.set_xlabel('Perturbation Technique')
    ax.set_ylabel('Number of Indexed Pages')
    for top_bar, bottom_bar in zip(top_bars, bottom_bars):
        top, bottom = top_bar.get_height(), bottom_bar.get_height()
        ax.annotate('M='+f'{top/(top+bottom):0.2f}'.lstrip('0').replace('1.00','1').replace('.00','0'),
                    xy=(top_bar.get_x() + top_bar.get_width() / 2, top+bottom),
                    xytext=(0, 3), # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.savefig('google_hiding.svg', bbox_inches='tight')
    plt.savefig('google_hiding.png', bbox_inches='tight')
    print('Hiding bar chart saved to google_hiding.[svg/png].')

def surfacing_graphs(pickle_file):
    # Load the pickle file
    with open(pickle_file, 'rb') as f:
        serps = pickle.load(f)['serps']

    count = Counter()
    for serp in serps:
        hit = 'miss'
        perturbation, article = '', ''
        o_perturbation = serp['query']['technique']
        o_article = serp['query']['article']
        if int(serp['result']['searchInformation']['totalResults']) > 0:
            for result in serp['result']['items']:
                url = result['link'].split('/')
                if (len(url) == 5): # Filters out homepage from results
                    perturbation = url[-2]
                    article = int(url[-1].split('.')[0])
                if perturbation == o_perturbation and article == o_article:
                    hit = 'hit'
                    break
        count[f'{o_perturbation}-{hit}'] += 1

    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 4)
    for idx, technique in enumerate(['base', 'zwsp', 'zwnj', 'zwj', 'rlo', 'bksp', 'del', 'homo']):
        pct = count[f'{technique}-hit']/max(count[f'{technique}-hit']+count[f'{technique}-miss'],1)
        axs[idx//4,idx%4].pie([pct,1-pct], autopct='%1.0f%%', colors=['lightsteelblue', 'lightcoral'])
        axs[idx//4,idx%4].set_title(technique)

    plt.legend(['Perturbed Target Present in SERP','Perturbed Target Absent in SERP'], loc='lower center', bbox_to_anchor=(-1.32,-1.25))
    fig.suptitle("Google:\nPerturbed Result from Perturbed Query", fontsize=16, y=1.05)

    plt.savefig('google_surfacing.svg', bbox_inches='tight')
    plt.savefig('google_surfacing.png', bbox_inches='tight')
    print('Surfacing pie charts saved to google_surfacing.[svg/png].')