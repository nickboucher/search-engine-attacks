#!/usr/bin/env python3
#
# indexing.py
# December 2022
#
# Utilities for indexing Simple Wikipedia. Should be called
# from the command line using elastic.py.
#
import wikitextparser as wtp
from html2text import html2text as htt
from constants import SIMPLE_WIKI_URL, TMP_FILE, ELASTIC_SETTINGS, ELASTIC_MAPPINGS
from re import sub
from urllib.request import urlopen
from os import remove
from shutil import copyfileobj
from bz2 import decompress
from tqdm import tqdm
from perturbations import perturbations, perturb_doc

def dewiki(text):
    text = wtp.parse(text).plain_text()  # wiki to plaintext 
    text = htt(text)  # remove any HTML
    text = text.replace('\\n',' ')  # replace newlines
    text = sub('\s+', ' ', text)  # replace excess whitespace
    return text

def analyze_chunk(text):
    try:
        if '<redirect title="' in text:  # this is not the main article
            return None
        if '(disambiguation)' in text:  # this is not an article
            return None
        else:
            title = text.split('<title>')[1].split('</title>')[0]
            title = htt(title)
            if ':' in title:  # most articles with : in them are not articles we care about
                return None
        serial = text.split('<id>')[1].split('</id>')[0]
        content = text.split('</text')[0].split('<text')[1].split('>', maxsplit=1)[1]
        content = dewiki(content)
        return {'title': title.strip(), 'body': content.strip(), 'article-id': serial.strip()}
    except Exception as oops:
        print(oops)
        return None

def save_article(elastic, article, id):
    doc = analyze_chunk(article)
    if doc:
        for perturbation in perturbations:
            elastic.index(index=perturbation, document=perturb_doc(doc, perturbation), id=f'{perturbation}-{id}')

def process_file_text(elastic, filename):
    article = ''
    id = 0
    with open(filename, 'r', encoding='utf-8') as infile:
        with tqdm(total=223660, desc='Indexing Articles') as pbar:
            for line in infile:
                if '<page>' in line:
                    article = ''
                elif '</page>' in line:  # end of article
                    save_article(elastic, article, id)
                    id += 1
                    pbar.update(1)
                else:
                    article += line                

def index(elastic):
    # Define temp files
    bz2_temp = TMP_FILE+'.bz2'
    xml_temp = TMP_FILE+'.xml'

    # Download the Simple Wikipedia dump
    print("Downloading archive...")
    with urlopen(SIMPLE_WIKI_URL) as response, open(bz2_temp, 'wb') as bz2:
        copyfileobj(response, bz2)

    # Extract the downloaded archive
    print("Extracting archive...")
    with open(bz2_temp, 'rb') as bz2, open(xml_temp, 'wb') as xml:
            xml.write(decompress(bz2.read()))

    # Delete compressed temp file
    print("Removing compressed archive...")
    remove(bz2_temp)

    print("Creating ElasticSearch Indices...")
    for perturbation in perturbations:
        elastic.indices.create(index=perturbation, settings=ELASTIC_SETTINGS, mappings=ELASTIC_MAPPINGS, ignore=400)

    # Process WikiXML into SQL
    print("Loading data into ElasticSearch Index...")
    process_file_text(elastic, xml_temp)

    # Delete decompressed temp file
    print("Removing extracted archive...")
    remove(xml_temp)

    # Confirm success
    print(f'Successfully built Simple Wikipedia Elasticsearch Index.')