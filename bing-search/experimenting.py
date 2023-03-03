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
import time
from tqdm.auto import tqdm
from datetime import datetime
from os.path import exists
from typing import Dict
from perturbations import perturb

# Programmable Search Engine IDs
engines = { 'srcf-all': '71a4c1af-7bba-480a-972e-b00c10726048',
            'srcf-base': '22b09131-e0f1-4797-9194-5064f0dde90b',
            'srcf-zwsp': 'dd4bd9fd-7d30-4753-8377-f743626c6d06',
            'srcf-zwnj': 'e6b3b2ad-923a-440a-93aa-b0aeaac14fcc',
            'srcf-zwj': 'd04ef597-b891-4848-b40e-2a3c20fdb99f',
            'srcf-rlo': '4042db65-2f13-41cb-b965-27a362280fea',
            'srcf-bksp': 'd67bf523-1f13-45a8-8fd2-6ea8c984371a',
            'srcf-del': 'be0b5695-192c-4b3a-bf8b-158cc8f97437',
            'srcf-homo': '60831fb2-aa00-4c31-b400-4a4d1c9ff10c',
            'srcf-zwsp2': '1145fdcc-402c-402e-b9a2-65a58d2383ed',
            'srcf-homo2': '448e1efc-6592-4335-ab9c-747ad884e734',
            'ml-all': 'f2514a2f-59ba-4611-99b0-2447a7010ddf',
            'ml-base': '7d92f108-99c7-4e35-b987-9c40fce8088b',
            'ml-zwsp': '6690bf97-b1ac-486d-a113-ea2d7d87355d',
            'ml-zwnj': '4cf2a6f9-b3be-4965-a5c8-f5c5c518ec36',
            'ml-zwj': 'a1fa89f1-5fc6-4eb3-ab41-04a9dd6e034e',
            'ml-rlo': 'eee9f6ca-8231-4cb9-a688-e05b8998cc7c',
            'ml-bksp': '8a954235-392c-424a-b337-99a3f7839a13',
            'ml-del': '246db391-4474-48d8-9e98-ff55b2b38d6d',
            'ml-homo': '0a3dcc43-c58d-469a-aaa5-dad0358ff1cb' }

# Indexed Artciles list manually extracted from Bing by searching for:
# site:{SITE_NAME}
# ...and combining the results of the following console script for each SERP:
# Array(...document.querySelectorAll('a')).map(el => el.href).filter(el => !el.includes("bing.com") && !el.includes("javascript:") && !el.includes("microsoft.com") && el)
srcf_articles = ['Hans Zender', 'Great Bentley', 'Jerrier A. Haddad', 'IPhone 5C', 'Shelley, Idaho', 'A Day in the Life', 'George Polk Awards', 'Helen Herron Taft', 'Gilles Latulippe', 'Kitty Hawk, North Carolina', 'Charlotte Rae', 'Vaudes', 'Battleship Potemkin', 'Oak Park, Illinois', 'Plouégat-Guérand', 'Leah Clark', 'Free market', 'Cullowhee, North Carolina', 'Herat', 'Seaca de Câmp', 'Oro y plata', 'Jerry Mathers', 'Greg Papa', 'Duško Popov', 'Sacheen Littlefeather', 'Daydreaming (song)', 'Sverigetopplistan', 'The Godfather Part II', 'Emerson, Lake and Powell', 'Paranthropus aethiopicus', 'Didí Torrico', 'Swan', 'Christine Keeler', 'Samir Farid', 'Canonical form', 'Christina Hendricks', 'Little India MRT station', 'Tracie Spencer', 'Luc-Adolphe Tiao', 'Christopher A. Wray', 'Nezapir', 'Yoram Globus', 'Joseph D. Pistone', 'Datsakorn Thonglao', 'COVID-19 pandemic in Missouri', 'Alan Shearer', 'Shanghai World Financial Center', 'Adam Deadmarsh', '65th British Academy Film Awards', 'Members Church of God International', 'Winter solstice', 'The Family Jewels (movie)', 'Gurtnellen', 'Soriano Department', '119 Tauri', 'Adelaide Kane', 'Frances Farenthold', 'Praça Diogo de Vasconcelos', 'Centennial Olympic Park bombing', 'La Pommeraie-sur-Sèvre', 'Mycoplasma genitalium', 'Dozwil', 'Leeds Cathedral', 'Cuts Both Ways', 'Chisago Lakes', 'Aberaeron', 'Enhanced Fujita scale', 'Cappy, Somme', 'King George V DLR station', 'Claw', 'Cremona', 'Insurance (constituency)', 'Waqar Ahmad Shah', 'Ed Westcott', 'Cerebellum', '1st century BC', 'Mateur', 'Gary Staples', 'List of A2 roads', 'Naked eye', 'Odra', 'Ross Ardern', 'Twist (dance)', '2019 NASCAR Xfinity Series', 'In-N-Out Burger', 'Selous&#39; zebra', 'Hillary Clinton', 'Jussy, Aisne', 'Provinces of Oman', 'Source code', 'Vätterstads IK', 'The Illustrated World of Mortal Engines', 'First Sino-Japanese War', 'Sainte-Suzanne-et-Chammes', 'Joël Bouchard', 'Dado Cavalcanti', 'Lucky Pulpit', 'Monte Plata Province', 'Glovelier', 'Cape Breton Island']
bing_srcf_indexed = [('srcf-base', 70), ('srcf-base', 3), ('srcf-base', 46), ('srcf-base', 83), ('srcf-del', 94), ('srcf-base', 5), ('srcf-del', 5), ('srcf-base', 60), ('srcf-bksp', 78), ('srcf-base', 50), ('srcf-base', 86), ('srcf-rlo', 44), ('srcf-rlo', 97), ('srcf-homo', 96), ('srcf-base', 39), ('srcf-bksp', 48), ('srcf-bksp', 66), ('srcf-base', 92), ('srcf-rlo', 32), ('srcf-base', 66), ('srcf-base', 36), ('srcf-base', 49), ('srcf-rlo', 10), ('srcf-bksp', 97), ('srcf-rlo', 22), ('srcf-rlo', 5), ('srcf-base', 54), ('srcf-rlo', 39), ('srcf-rlo', 27), ('srcf-del', 56), ('srcf-base', 56), ('srcf-rlo', 3), ('srcf-del', 70), ('srcf-del', 83), ('srcf-bksp', 92), ('srcf-del', 76), ('srcf-base', 78), ('srcf-base', 97), ('srcf-rlo', 92), ('srcf-rlo', 69), ('srcf-homo', 85), ('srcf-homo', 55), ('srcf-del', 2), ('srcf-rlo', 49)]
bing_ml_indexed = [('ml-base', '2021 Peru bus crash'), ('ml-base', 'Milada Horáková'), ('ml-base', 'Harry Potter and the Half-Blood Prince'), ('ml-base', 'Stonehenge, Avebury and Associated Sites'), ('ml-base',  'British Rail locomotive and multiple unit numbering and classification'), ('ml-base', "Earth's magnetic field"), ('ml-base', "Schrödinger's cat"), ('ml-base', 'Merv Griffin'), ('ml-base', 'Pyrénées-Atlantiques'), ('ml-base', 'Abstinence'), ('ml-base', 'Juan Guaidó'), ('ml-base', 'Nestlé'), ('ml-base', 'José S Carrión'), ('ml-base', 'Non-coding DNA'), ('ml-base', 'Abutilon'), ('ml-base', 'Zdeněk Hoření'), ('ml-base', 'Disgrace of Gijón'), ('ml-base', 'Diaper'), ('ml-base', '2011 Tōhoku earthquake and tsunami'), ('ml-base', "Joule's laws"), ('ml-base', "Queen's Hall"), ('ml-base', 'List of countries and dependencies by population density'), ('ml-rlo', 'BioShock'), ('ml-base', 'Branko Kostić'), ('ml-base', 'Medusa with the Head of Perseus'), ('ml-base', 'Mazatlán'), ('ml-base', 'J.B.S. Haldane'), ('ml-rlo', 'Isekai'), ('ml-base', 'Ocean thermal energy conversion'), ('ml-base', 'Rifat Hadžiselimović'), ('ml-base', 'Apicomplexa'), ('ml-base', "Faraday's laws of electrolysis"), ('ml-base', 'Kashima-jingū'), ('ml-base', "Newton's laws of motion"), ('ml-homo', 'Brass'), ('ml-homo', 'Pier'), ('ml-base', 'Hōgen (era)'), ('ml-homo', 'Hossam Ashour'), ('ml-base', 'Stuyvesant Town–Peter Cooper Village'), ('ml-base', 'Transistor–transistor logic'), ('ml-base', 'Anais García Balmaña'), ('ml-base', 'Miloš Radulović'), ('ml-base', 'Claude Lévi-Strauss'), ('ml-base', 'Mária Pozsonec'), ('ml-base', 'Cobalt(III) fluoride'), ('ml-base', 'Ramanuja Devnathan'), ('ml-base', "Student's t-test"), ('ml-homo', 'Type species'), ('ml-base', 'Shojiro Sugimura'), ('ml-base', '2022 FIFA World Cup'), ('ml-base', 'Cobalt(III) fluoride'), ('ml-base', 'Ramanuja Devnathan'), ('ml-base', 'Shojiro Sugimura'), ('ml-base', 'Zenani Mandela-Dlamini'), ('ml-base', 'Beril Dedeoğlu'), ('ml-zwsp', 'George Metallinos'), ('ml-zwnj', 'Tenpyō-kanpō'), ('ml-zwnj', 'Han Buddhism'), ('ml-zwnj', 'East Asian calligraphy'), ('ml-zwnj', 'List of tallest buildings in China'), ('ml-zwnj', 'Donald Adamson'), ('ml-zwnj', 'Type 14 105 mm cannon'), ('ml-zwsp', 'Claudine Monteil'), ('ml-zwj', 'Chitetsu Watanabe'), ('ml-zwsp', 'Council areas of Scotland'), ('ml-zwnj', 'Arrondissement of La Rochelle'), ('ml-zwnj', 'Diekirch (canton)'), ('ml-zwsp', 'The Million Pound Drop Live'), ('ml-zwj', 'Beatová síň slávy'), ('ml-zwj', 'Tōkaidō Shinkansen'), ('ml-zwj', 'Circuit (political division)'), ('ml-zwsp', 'National Anthem of the Republic of China'), ('ml-zwsp', 'Kōō (Nanboku-chō period)'), ('ml-zwnj', 'Principality of the Pindus'), ('ml-zwsp', 'The Collection 1982-1988'), ('ml-zwnj', 'Comunità montana Walser Alta Valle del Lys'), ('ml-zwsp', 'Leader of the Opposition (Japan)'), ('ml-zwsp', 'Kitzingen (district)'), ('ml-zwnj', 'Arrondissement of Lille'), ('ml-zwj', 'Prime Minister of Singapore'), ('ml-zwj', 'Kangding Qingge'), ('ml-zwsp', 'Arrondissement of Brive-la-Gaillarde'), ('ml-zwsp', 'King Tang of Shang of China'), ('ml-zwj', 'Type 95 75 mm field gun'), ('ml-zwnj', 'Tōkaidō (region)'), ('ml-zwj', 'Empress Myeongseong'), ('ml-zwnj', 'Bremgarten (district)'), ('ml-zwj', 'Lenzburg (district)'), ('ml-zwj', '2006 Hengchun earthquakes'), ('ml-zwj', 'Nagasaki Prefecture'), ('ml-zwj', 'Carbon–hydrogen bond activation'), ('ml-zwnj', 'List of speakers of the House of Representatives (Japan)'), ('ml-zwsp', 'Densha de Go! (series)'), ('ml-zwj', 'Cabinet of Germany'), ('ml-zwsp', 'Tenshō (Momoyama period)'), ('ml-zwsp', '2013–14 Fußball-Bundesliga'), ('ml-zwj', 'Coligny calendar'), ('ml-zwj', 'Japanese Imperial year'), ('ml-zwsp', '100 Landscapes of Japan (Shōwa period)')]

def experiment(site: str, key_file: str, experiment_name: str) -> None:
    srcf = False
    ml = False
    match site:
        case 'srcf': srcf = True
        case 'ml': ml = True
        case 'all': srcf, ml = True, True
        case _ : raise ValueError(f'Unknown site: {site}')
    with open(key_file, 'r') as f:
        global key
        key = f.read()
    match experiment_name:
        case 'hiding': hiding_experiment(srcf, ml)
        case 'surfacing': surfacing_experiment(srcf, ml)
        case 'all': hiding_experiment(srcf, ml); surfacing_experiment(srcf, ml)
        case _ : raise ValueError(f'Unknown experiment: {experiment_name}')

def hiding_experiment(srcf: bool, ml: bool) -> None:
    if srcf:
        hiding_srcf_experiment()
    if ml:
        hiding_ml_experiment()

def hiding_srcf_experiment():
    filename = f'bing-srcf_serps_hiding-{datetime.now().strftime("%Y-%m-%d")}.pkl'
    if exists(filename):
        print('Loading previous SRCF results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = pickle.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = len(bing_srcf_indexed)
    write_interval = count // 20 # Write every 5% of the way through

    for i, (technique, article) in tqdm(enumerate(bing_srcf_indexed), total=count, desc='SRCF Hiding Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        serp = search(engines[technique], srcf_articles[article])
        serps.append({
            'query': {
                'article': article,
                'technique': technique,
                'title': srcf_articles[article]
            },
            'result': serp
        })
        time.sleep(1.25)

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_pickle(filename, serps, srcf_articles)

    # Write final results to file
    write_pickle(filename, serps, srcf_articles)
    print(f'Hiding SRCF experiment complete. Results written to {filename}.')

def hiding_ml_experiment():
    filename = f'bing-ml_serps_hiding-{datetime.now().strftime("%Y-%m-%d")}.pkl'
    if exists(filename):
        print('Loading previous ML results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = pickle.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = len(bing_ml_indexed)
    write_interval = count // 20 # Write every 5% of the way through

    for i, (technique, article) in tqdm(enumerate(bing_ml_indexed), total=count, desc='ML Hiding Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        serp = search(engines[technique], article)
        serps.append({
            'query': {
                'technique': technique,
                'title': article
            },
            'result': serp
        })
        time.sleep(1.25)

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_pickle(filename, serps)

    # Write final results to file
    write_pickle(filename, serps)
    print(f'Hiding ML experiment complete. Results written to {filename}.')

def surfacing_experiment(srcf: bool, ml: bool) -> None:
    if srcf:
        surfacing_srcf_experiment()
    if ml:
        surfacing_ml_experiment()

def surfacing_srcf_experiment():
    filename = f'bing-srcf_serps_surfacing-{datetime.now().strftime("%Y-%m-%d")}.pkl'
    if exists(filename):
        print('Loading previous SRCF results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = pickle.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = len(bing_srcf_indexed)
    write_interval = count // 20 # Write every 5% of the way through

    for i, (technique, article) in tqdm(enumerate(bing_srcf_indexed), total=count, desc='SRCF Surfacing Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        perturbed = perturb(srcf_articles[article], technique.replace('srcf-',''))
        serp = search(engines['srcf-all'], perturbed)
        serps.append({
            'query': {
                'article': article,
                'technique': technique,
                'title': perturbed
            },
            'result': serp
        })
        time.sleep(1.25)

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_pickle(filename, serps, srcf_articles)

    # Write final results to file
    write_pickle(filename, serps, srcf_articles)
    print(f'Surfacing SRCF experiment complete. Results written to {filename}.')

def surfacing_ml_experiment():
    filename = f'bing-ml_serps_surfacing-{datetime.now().strftime("%Y-%m-%d")}.pkl'
    if exists(filename):
        print('Loading previous ML results from file to continue experiment...')
        with open(filename, 'rb') as f:
            serps = pickle.load(f)['serps']
    else:
        serps = []
    skip = len(serps)
    count = len(bing_ml_indexed)
    write_interval = count // 20 # Write every 5% of the way through

    for i, (technique, article) in tqdm(enumerate(bing_ml_indexed), total=count, desc='ML Surfacing Experiment'):
        # Skip any results already written to file
        if i < skip:
            continue

        perturbed = perturb(article, technique.replace('ml-',''))
        serp = search(engines['ml-all'], perturbed)
        serps.append({
            'query': {
                'technique': technique,
                'title': perturbed,
                'unperturbed_title': article
            },
            'result': serp
        })
        time.sleep(1.25)

        # Write results to file every 5% of the way through
        if i % write_interval == 0:
            write_pickle(filename, serps)

    # Write final results to file
    write_pickle(filename, serps)
    print(f'Surfacing ML experiment complete. Results written to {filename}.')

def search(engine: str, query: str) -> Dict:
  """ Run the supplied query against the selected private Bing engine. """
  url =  'https://api.bing.microsoft.com/v7.0/custom/search?'\
        f'q={query}&customconfig={engine}'
  headers = {'Ocp-Apim-Subscription-Key': bing_key}
  return requests.get(url, headers=headers).json()

def results(engine: str, query: str) -> int:
  """ Get the number of results for the supplied query against the selected
      private search engine. """
  return search(engine, query)['searchInformation']['totalResults']

def write_pickle(filename, serps, articles=None):
    with open(filename, 'wb') as f:
        if articles:
            pickle.dump({
                'articles': articles,
                'serps': serps
            }, f)
        else:
            pickle.dump({
                'serps': serps
            }, f)