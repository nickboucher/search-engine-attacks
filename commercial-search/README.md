# Commercial Search

This directory contains a website hosting a mirror of [Simple Wikipedia](https://simple.wikipedia.org). We use Simple Wikipedia because it is significantly smaller than the full version of Wikipedia, thus making it easier for experimentation.

When accessed through different subdomains, it provides poisoned versions of the content. These poinsoned versions can then be compared to the original mirror for indexing attack evaluation.

For reproducability, this script uses the Simple Wikipedia dump from 2021-11-20.

## Installation

Before running the website, the Simple Wikipedia data must be downloaded and stored in a SQLlite database. This only needs to be done once, and can be performed with:

```
./setup.py
```
This script is largely based on David Shapiro's [PlainTextWikipedia](https://github.com/daveshap/PlainTextWikipedia).