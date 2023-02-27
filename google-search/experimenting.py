#!/usr/bin/env python3
#
# experimenting.py
# February 2023
#
# Utilities for searching experimental queries against perturbed
# Simple Wikipedia. Should be called from the command line using elastic.py.
#
import pickle
import requests
import csv
import time
from tqdm.auto import tqdm
from datetime import datetime
from os.path import exists
from perturbations import perturb

# Programmable Search Engine IDs
engines = {'all': '142159d18e7ba4f76',
           'base': 'd0b4654ffe2ddd973',
           'zwsp': '696b398ef696a33df',
           'zwnj': '837d8a77950e8c20c',
           'zwj': '035bd5a64cd3b4ef8',
           'rlo': 'a558d120a88c81a7f',
           'bksp': 'c4e6ced42346ccd0b',
           'del': '8c9425d40016fbea6',
           'homo': '183dc363986e64fb5' }

# Articles Contained in Deployed Bad Search Wiki
articles = ['Hans Zender', 'Great Bentley', 'Jerrier A. Haddad', 'IPhone 5C', 'Shelley, Idaho', 'A Day in the Life', 'George Polk Awards', 'Helen Herron Taft', 'Gilles Latulippe', 'Kitty Hawk, North Carolina', 'Charlotte Rae', 'Vaudes', 'Battleship Potemkin', 'Oak Park, Illinois', 'Plouégat-Guérand', 'Leah Clark', 'Free market', 'Cullowhee, North Carolina', 'Herat', 'Seaca de Câmp', 'Oro y plata', 'Jerry Mathers', 'Greg Papa', 'Duško Popov', 'Sacheen Littlefeather', 'Daydreaming (song)', 'Sverigetopplistan', 'The Godfather Part II', 'Emerson, Lake and Powell', 'Paranthropus aethiopicus', 'Didí Torrico', 'Swan', 'Christine Keeler', 'Samir Farid', 'Canonical form', 'Christina Hendricks', 'Little India MRT station', 'Tracie Spencer', 'Luc-Adolphe Tiao', 'Christopher A. Wray', 'Nezapir', 'Yoram Globus', 'Joseph D. Pistone', 'Datsakorn Thonglao', 'COVID-19 pandemic in Missouri', 'Alan Shearer', 'Shanghai World Financial Center', 'Adam Deadmarsh', '65th British Academy Film Awards', 'Members Church of God International', 'Winter solstice', 'The Family Jewels (movie)', 'Gurtnellen', 'Soriano Department', '119 Tauri', 'Adelaide Kane', 'Frances Farenthold', 'Praça Diogo de Vasconcelos', 'Centennial Olympic Park bombing', 'La Pommeraie-sur-Sèvre', 'Mycoplasma genitalium', 'Dozwil', 'Leeds Cathedral', 'Cuts Both Ways', 'Chisago Lakes', 'Aberaeron', 'Enhanced Fujita scale', 'Cappy, Somme', 'King George V DLR station', 'Claw', 'Cremona', 'Insurance (constituency)', 'Waqar Ahmad Shah', 'Ed Westcott', 'Cerebellum', '1st century BC', 'Mateur', 'Gary Staples', 'List of A2 roads', 'Naked eye', 'Odra', 'Ross Ardern', 'Twist (dance)', '2019 NASCAR Xfinity Series', 'In-N-Out Burger', 'Selous&#39; zebra', 'Hillary Clinton', 'Jussy, Aisne', 'Provinces of Oman', 'Source code', 'Vätterstads IK', 'The Illustrated World of Mortal Engines', 'First Sino-Japanese War', 'Sainte-Suzanne-et-Chammes', 'Joël Bouchard', 'Dado Cavalcanti', 'Lucky Pulpit', 'Monte Plata Province', 'Glovelier', 'Cape Breton Island']

def experiment(table, key_file, experiment_name):
    with open(key_file, 'r') as f:
        global key
        key = f.read()
    google_indexed = []
    with open(table) as csvfile:
        content = csv.reader(csvfile)
        for row in content:
            url = row[0].split('/')
            if (len(url) == 5):
                google_indexed.append((url[-2], int(url[-1].split('.')[0])))
    match experiment_name:
        case 'hiding': hiding_experiment(google_indexed, key)
        case 'surfacing': surfacing_experiment(google_indexed, key)
        case 'all': hiding_experiment(google_indexed, key); surfacing_experiment(google_indexed, key)
        case _ : raise ValueError(f'Unknown experiment: {experiment_name}')

def hiding_experiment(google_indexed):
    filename = f'google_serps_hiding-{datetime.now().strftime("%Y-%m-%d")}.pkl'
    if exists(filename):
        print('Loading previous results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = pickle.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = len(google_indexed)
    write_interval = count // 20 # Write every 5% of the way through

    for i, (technique, article) in tqdm(enumerate(google_indexed), total=count, desc='Hiding Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        serp = search(engines[technique], articles[article])
        serps.append({
            'query': {
                'article': article,
                'technique': technique,
                'title': articles[article]
            },
            'result': serp
        })
        time.sleep(0.5)

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_pickle(filename, serps)

    # Write final results to file
    write_pickle(filename, serps)
    print(f'Hiding experiment complete. Results written to {filename}.')

def surfacing_experiment(google_indexed, key):
    filename = f'google_serps_surfacing-{datetime.now().strftime("%Y-%m-%d")}.pkl'
    if exists(filename):
        print('Loading previous results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = pickle.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = len(google_indexed)
    write_interval = count // 20 # Write every 5% of the way through

    for i, (technique, article) in tqdm(enumerate(google_indexed), total=count, desc='Hiding Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        perturbed = perturb(articles[article], technique)
        serp = search(engines['all'], perturbed)
        serps.append({
            'query': {
                'article': article,
                'technique': technique,
                'title': perturbed
            },
            'result': serp
        })
        time.sleep(0.5)

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_pickle(filename, serps)

    # Write final results to file
    write_pickle(filename, serps)
    print(f'Surfacing experiment complete. Results written to {filename}.')

def search(engine: str, query: str) -> str:
  """ Run the supplied query against the selected private search engine. """
  url =  'https://www.googleapis.com/customsearch/v1?'\
        f'key={key}&cx={engine}&q={query}'
  return requests.get(url).json()

def results(engine: str, query: str) -> int:
  """ Get the number of results for the supplied query against the selected
      private search engine. """
  return search(engine, query)['searchInformation']['totalResults']

def write_pickle(filename, serps):
    with open(filename, 'wb') as f:
        pickle.dump({
            'articles': articles,
            'serps': serps
        }, f)