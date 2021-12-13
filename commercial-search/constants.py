#!/usr/bin/env python3
#
# setup.py
# Nicholas Boucher - December 2021
# Downloads SimpleWikipedia dump and loads into SQLite DB.
#
SIMPLE_WIKI_URL = 'https://dumps.wikimedia.org/simplewiki/20211201/simplewiki-20211201-pages-articles-multistream.xml.bz2'

TMP_FILE = './simplewiki'

SQL_DB = 'simplewiki.db'