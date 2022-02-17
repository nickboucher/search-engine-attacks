#!/usr/bin/env python3
#
# setup.py
# Nicholas Boucher - December 2021
# Downloads SimpleWikipedia dump and loads into SQL DB.
#
from typing import Iterator
import click
from flask.cli import with_appcontext
from urllib.request import urlopen
from shutil import copyfileobj
from os import remove
from bz2 import decompress
from re import sub
from html2text import html2text as htt
import wikitextparser as wtp
from tqdm import tqdm
from models import Article
from constants import SIMPLE_WIKI_URL, TMP_FILE
from app import db
from xml_sitemap_writer import XMLSitemap
from perturbations import perturb, perturbations
from urllib.parse import quote
from dotenv import dotenv_values
from os import makedirs
from shutil import rmtree

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
        return {'title': title.strip(), 'text': content.strip(), 'id': serial.strip()}
    except Exception as oops:
        print(oops)
        return None

def save_article(article):
    doc = analyze_chunk(article)
    if doc:
        entry = Article(doc['id'], doc['title'], doc['text'])
        db.session.add(entry)
        db.session.commit()

def process_file_text(filename):
    article = ''
    # Create table
    db.create_all()
    # Delete existing exntries, if any
    Article.query.delete()
    with open(filename, 'r', encoding='utf-8') as infile:
        for line in tqdm(infile, desc="Processing Export"):
            if '<page>' in line:
                article = ''
            elif '</page>' in line:  # end of article
                save_article(article)
            else:
                article += line                

@click.command('load-db')
@with_appcontext
def load_db():
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

    # Process WikiXML into SQL
    print("Loading data into SQL DB...")
    process_file_text(xml_temp)

    # Delete decompressed temp file
    print("Removing extracted archive...")
    remove(xml_temp)

    # Confirm success
    print(f'Successfully built Simple Wikipedia database.')

@click.command('gen-sitemaps')
@with_appcontext
def gen_sitemaps():
    print("Building sitemaps...")
    sitemaps = 'static/sitemaps'
    server = dotenv_values()["SERVER_NAME"]
    rmtree(sitemaps, ignore_errors=True)
    makedirs(sitemaps)
    with open(f'{sitemaps}/sitemap.xml', 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for perturbation in perturbations:
            f.write(f'<url><loc>https://{perturbation}.{server}</loc></url>\n')
        f.write('</urlset>\n')
    for perturbation in perturbations:
        def get_urls() -> Iterator[str]:
            for article in db.session.query(Article.title).yield_per(1000):
                yield f'/article/{quote(perturb(article["title"], perturbation))}'
        path = f'{sitemaps}/{perturbation}'
        makedirs(path, exist_ok=True)
        with XMLSitemap(path=path, root_url=f'https://{perturbation}.{server}') as sitemap:
            sitemap.add_urls(get_urls())
        with open(f'{path}/sitemap.xml', 'r') as f:
            sitemap = f.read()
        with open(f'{path}/sitemap.xml', 'w') as f:
            f.write(sitemap.replace(f'https://{perturbation}.{server}', f'https://{perturbation}.{server}/sitemaps'))   
    print("Sitemap building complete.")