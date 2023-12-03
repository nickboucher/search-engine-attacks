#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from nltk.translate.chrf_score import corpus_chrf

def main():
    # Main Parser
    parser = ArgumentParser(description='Adversarial Search Experiments using the Google Bard Chatbot.')
    parser.add_argument('json_file', help='JSON file of experimental results for building graphs.')
    
    # Parse arguments
    args = parser.parse_args()

    # Invoke function to build graphs
    graphs(args.json_file)

def url_set(urls: list[str]) -> set[str]:
    '''Convert a list of URLs to a set of URLs without the protocol.'''
    return set(map(lambda url: url.split('://')[1], urls))

def graphs(json_file: str) -> None:
    # Load the pickle file
    with open(json_file, 'r') as f:
        results = json.load(f)

    bases = list(filter(lambda x: x['query']['technique'] == 'base', results))
    bases_text = { base['query']['title']:base['result']['response'] for base in bases }
    bases_urls = { base['query']['title']:url_set(base['result']['sources']) for base in bases }

    performance = {}
    urls = {}
    for result in results:
        # Create result holder
        technique = result['query']['technique']
        title = result['query']['title']
        if technique not in performance:
            performance[technique] = { 'chrf': 0, 'total': 0 }
        if technique not in urls:
            urls[technique] = { 'disruption': 0, 'total': 0 }
        # Remove citations from result
        result_text = result['result']['response']
        base_text = bases_text[title]
        # Calculate CHRF score
        performance[technique]['total'] += 1
        performance[technique]['chrf'] += corpus_chrf([base_text], [result_text])
        # Store result URLs
        result_urls = url_set(result['result']['sources'])
        intersect = result_urls.intersection(bases_urls[title])
        urls[technique]['total'] += len(result_urls)
        urls[technique]['disruption'] += len(intersect)

    # Plot CHRF scores
    plt.style.use('ggplot')
    values = list(zip(performance.keys(), [score['chrf']/score['total'] for score in performance.values()]))
    values.sort(key=lambda x: -x[1])
    x,y = tuple(zip(*values))
    _, ax = plt.subplots()
    ax.bar(x, y, color='dodgerblue')
    ax.set_title('Google Bard Chatbot:\nOutput Comparison for Perturbed Inputs', fontsize=16, y=1.06)
    ax.set_xlabel('Perturbation Technique')
    ax.set_ylabel('chrF Score\nwith output from unperturbed input')

    plt.savefig('google-bard_chrf.svg', bbox_inches='tight')
    plt.savefig('google-bard_chrf.png', bbox_inches='tight')
    plt.savefig('google-bard_chrf.pdf', bbox_inches='tight')
    print('chrF bar chart saved to google-bard_chrf.[svg/png/pdf].')

    # Plot disruption scores
    nonzero_urls = { technique:score for technique, score in urls.items() if score['total'] > 0 }
    plt.style.use('ggplot')
    values = list(zip(nonzero_urls.keys(), [1-(score['disruption']/score['total']) for score in nonzero_urls.values()]))
    values.sort(key=lambda x: -x[1])
    x,y = tuple(zip(*values))
    _, ax = plt.subplots()
    ax.set_ylim([0,1.1])
    ax.bar(x, y, color='dodgerblue')
    ax.set_title('Google Bard Chatbot:\nCitation Comparison for Perturbed Inputs', fontsize=16, y=1.06)
    ax.set_xlabel('Perturbation Technique')
    ax.set_ylabel('Disruption Potential ($M_d$)')

    plt.savefig('google-bard_disruption.svg', bbox_inches='tight')
    plt.savefig('google-bard_disruption.png', bbox_inches='tight')
    plt.savefig('google-bard_disruption.pdf', bbox_inches='tight')
    print('Disruption bar chart saved to bing-chat_disruption.[svg/png/pdf].')

if __name__ == '__main__':
    main()