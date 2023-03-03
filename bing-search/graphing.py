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
from urllib.parse import unquote
from perturbations import unperturb

def graphs(experiment_name: str, srcf_pickle_file: str, ml_pickle_file: str) -> None:
    match experiment_name:
        case 'hiding': hiding_graphs(srcf_pickle_file, ml_pickle_file)
        case 'surfacing': surfacing_graphs(srcf_pickle_file, ml_pickle_file)
        case 'all': hiding_graphs(srcf_pickle_file, ml_pickle_file); surfacing_graphs(srcf_pickle_file, ml_pickle_file)
        case _ : raise ValueError(f'Unknown experiment: {experiment_name}')

def hiding_graphs(srcf_pickle_file: str, ml_pickle_file: str) -> None:
    # Load the SRCF pickle file
    srcf_performance = {}
    if srcf_pickle_file:
        with open(srcf_pickle_file, 'rb') as f:
            srcf_serps = pickle.load(f)['serps']
        for technique in ['srcf-base','srcf-zwsp','srcf-zwnj','srcf-zwj','srcf-rlo','srcf-bksp','srcf-del','srcf-homo']:
            srcf_performance[technique] = { 'success': 0, 'total': 0 }
        for serp in srcf_serps:
            technique = serp['query']['technique']
            srcf_performance[technique]['total'] += 1
            if 'webPages' in serp['result']:
                for page in serp['result']['webPages']['value']:
                    url = page['url'].split('/')
                    if len(url) == 5:
                        if int(url[-1].split('.')[0]) == serp['query']['article']:
                            srcf_performance[technique]['success'] += 1

    # Load the ML pickle file
    ml_performance = {}
    if ml_pickle_file:
        with open(ml_pickle_file, 'rb') as f:
            ml_serps = pickle.load(f)['serps']
        for technique in ['ml-base','ml-zwsp','ml-zwnj','ml-zwj','ml-rlo','ml-bksp','ml-del','ml-homo']:
            ml_performance[technique] = { 'success': 0, 'total': 0 }
        for serp in ml_serps:
            technique = serp['query']['technique']
            ml_performance[technique]['total'] += 1
            if 'webPages' in serp['result']:
                for page in serp['result']['webPages']['value']:
                    url = page['url'].split('/')
                    if len(url) == 5:
                        if unperturb(unquote(url[-1].split('.')[0]),url[2].split('.')[0]) == serp['query']['title']:
                            ml_performance[technique]['success'] += 1
    # Combine results
    performance = ml_performance
    for k,v in srcf_performance.items():
        performance[k.replace('srcf-', 'ml-')]['success'] += v['success']
        performance[k.replace('srcf-', 'ml-')]['total'] += v['total']

    # Build the graph
    values = list(zip(performance.keys(),
                  map(lambda x: x['success'], performance.values()),
                  map(lambda x: x['total'] - x['success'], performance.values())))
    values.sort(key=lambda x: -x[1]-x[2])
    x,y1,y2 = tuple(zip(*values))
    x = list(map(lambda x: x.replace('ml-',''), x))

    plt.style.use('ggplot')
    _, ax = plt.subplots()
    top_bars = ax.bar(x, y1, label='Perturbed Target Present in SERP', color='lightseagreen', bottom=y2)
    bottom_bars = ax.bar(x, y2, label='Perturbed Target Absent in SERP', color='tomato')
    ax.set_ylim([0,79])
    ax.legend(loc='lower center', bbox_to_anchor=(.5,-.31))
    ax.set_title('Bing:\nPerturbed Index & Unperturbed Queries', fontsize=16, y=1.06)
    ax.set_xlabel('Perturbation Technique')
    ax.set_ylabel('Number of Indexed Pages')
    for top_bar, bottom_bar in zip(top_bars, bottom_bars):
        top, bottom = top_bar.get_height(), bottom_bar.get_height()
        ax.annotate('M='+f'{top/(top+bottom):0.2f}'.lstrip('0').replace('1.00','1').replace('.00','0'),
                    xy=(top_bar.get_x() + top_bar.get_width() / 2, top+bottom),
                    xytext=(0, 3), # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    plt.savefig('bing_hiding.svg', bbox_inches='tight')
    plt.savefig('bing_hiding.png', bbox_inches='tight')
    print('Hiding bar chart saved to bing_hiding.[svg/png].')

def surfacing_graphs(srcf_pickle_file: str, ml_pickle_file: str) -> None:
    # Load the SRCF pickle file
    srcf_count = Counter()
    if srcf_pickle_file:
        with open(srcf_pickle_file, 'rb') as f:
            srcf_serps = pickle.load(f)['serps']
        for serp in srcf_serps:
            hit = 'miss'
            perturbation, article = '', ''
            o_perturbation = serp['query']['technique'].replace('srcf-','')
            o_article = serp['query']['article']
            results = len(serp['result']['webPages']['value']) if 'webPages' in serp['result'] else 0
            if results > 0:
                for result in serp['result']['webPages']['value']:
                    url = result['url'].split('/')
                    if (len(url) == 5): # Filters out homepage from results
                        perturbation = url[-2]
                        article = int(url[-1].split('.')[0])
                    if perturbation == o_perturbation and article == o_article:
                        hit = 'hit'
                        break
            srcf_count[f'{o_perturbation}-{hit}'] += 1

    # Load the ML pickle file
    ml_count = Counter()
    if ml_pickle_file:
        with open(ml_pickle_file, 'rb') as f:
            ml_serps = pickle.load(f)['serps']
        for serp in ml_serps:
            hit = 'miss'
            perturbation, article = '', ''
            o_perturbation = serp['query']['technique'].replace('ml-','')
            o_article = serp['query']['unperturbed_title']
            results = len(serp['result']['webPages']['value']) if 'webPages' in serp['result'] else 0
            if results > 0:
                for result in serp['result']['webPages']['value']:
                    url = result['url'].split('/')
                    if (len(url) == 5): # Filters out homepage from results
                        perturbation = url[2].split('.')[0]
                        article = unperturb(unquote(url[-1].split('.')[0]),perturbation)
                    if perturbation == o_perturbation and article == o_article:
                        hit = 'hit'
                        break
            ml_count[f'{o_perturbation}-{hit}'] += 1

    # Combine results
    count = ml_count
    for k,v in srcf_count.items():
        count[k] += v

    # Build the graph
    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 4)
    for idx, technique in enumerate(['base', 'zwsp', 'zwnj', 'zwj', 'rlo', 'bksp', 'del', 'homo']):
        pct = count[f'{technique}-hit']/max(count[f'{technique}-hit']+count[f'{technique}-miss'],1)
        axs[idx//4,idx%4].pie([pct,1-pct], autopct='%1.0f%%', colors=['lightseagreen', 'tomato'])
        axs[idx//4,idx%4].set_title(technique)
    plt.legend(['Perturbed Target Present in SERP','Perturbed Target Absent in SERP'], loc='lower center', bbox_to_anchor=(-1.32,-1.32))
    fig.suptitle("Bing:\nPerturbed Result from Perturbed Query", fontsize=16, y=1.05)
    plt.savefig('bing_surfacing.svg', bbox_inches='tight')
    plt.savefig('bing_surfacing.png', bbox_inches='tight')
    print('Surfacing pie charts saved to bing_surfacing.[svg/png].')
