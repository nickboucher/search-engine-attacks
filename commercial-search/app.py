#!/usr/bin/env python3
#
# application.py
# Nicholas Boucher - December 2021
# Flask server app for SimpleWiki clone.
#
from flask import Flask, render_template, request, abort
from dotenv import dotenv_values
from urllib.parse import unquote
from typing import List
from models import db, Article
from cli import load_db
from perturbations import perturbations, unperturb

app = Flask(__name__)
for key, val in dotenv_values().items():
    app.config[key] = val
db.init_app(app)
app.cli.add_command(load_db)

@app.route("/")
def subdomain_list():
    return render_template('subdomain_list.html', subdomains=perturbations, host=request.host)

@app.route("/", subdomain="<perturbation>")
@app.route("/<int:page>", subdomain="<perturbation>")
def article_list(perturbation, page=1):
    # Query only titles for efficiency
    articles = db.session.query(Article.title).paginate(page,25)
    if not articles.items:
        abort(404)
    for i, article in enumerate(articles.items):
        articles.items[i] = Article(0, article['title'], '').perturb(perturbation)
    return render_template('article_list.html', articles=articles)

@app.route("/article/<title>", subdomain="<perturbation>")
def article(title, perturbation):
    article = Article.query.filter_by(title=unperturb(unquote(title), perturbation)).first()
    if not article:
        abort(404)
    article.perturb(perturbation)
    return render_template('article.html', article=article)