#!/usr/bin/env python3
#
# application.py
# Nicholas Boucher - December 2021
# Flask server app for SimpleWiki clone.
#
from flask import Flask, render_template, request, abort
from dotenv import dotenv_values
from urllib.parse import quote, unquote
from typing import List
from models import db, Article
from cli import load_db

app = Flask(__name__)
for key, val in dotenv_values().items():
    app.config[key] = val
db.init_app(app)
app.cli.add_command(load_db)

subdomains = ['base']

def perturb(articles: List[Article]|Article, perturbation: str, perturb_text=True) -> None:
    def _perturb(input: str) -> str:
        match perturbation:
            case 'base' : return input
            case _ : abort(404)
    if articles:
        if isinstance(articles, Article) : articles = [articles]
        for article in articles:
            _perturb(article.title)
            if perturb_text : _perturb(article.text)

@app.route("/")
def subdomain_list():
    return render_template('subdomain_list.html', subdomains=subdomains, host=request.host)

@app.route("/", subdomain="<perturbation>")
@app.route("/<int:page>", subdomain="<perturbation>")
def article_list(perturbation, page=1):
    articles = db.session.query(Article.title).order_by(Article.title.asc()).paginate(page,25,error_out=False).items
    if not articles:
        abort(404)
    perturb(articles, perturbation, False)
    return render_template('article_list.html', articles=articles, quote=quote, page=page)

@app.route("/article/<title>", subdomain="<perturbation>")
def article(title, perturbation):
    article = Article.query.filter_by(title=unquote(title)).first()
    if not article:
        abort(404)
    perturb(article, perturbation)
    return render_template('article.html', article=article)