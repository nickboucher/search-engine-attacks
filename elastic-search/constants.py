#!/usr/bin/env python3
#
# constants.py
# Nicholas Boucher - December 2021
# Constant values for SimpleWiki clone.
#
SIMPLE_WIKI_URL = 'https://dumps.wikimedia.org/simplewiki/20221201/simplewiki-20221201-pages-articles-multistream.xml.bz2'

TMP_FILE = './simplewiki'

ELASTIC_SETTINGS = {
        "number_of_shards": 2,
        "number_of_replicas": 1
    }

ELASTIC_MAPPINGS = {
        "properties": {
            "article-id": {
                "type": "text",
                "index": False
            },
            "title": {
                "type": "text"
            },
            "body": {
                "type": "text"
            }
        }
    }