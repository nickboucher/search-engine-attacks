#!/usr/bin/env python3
#
# application.py
# Nicholas Boucher - December 2021
# Flask server app for SimpleWiki clone.
#
from flask import Flask, render_template, request, abort, send_from_directory
from dotenv import dotenv_values
from urllib.parse import unquote
from models import db, Article
from cli import load_db, gen_sitemaps
from perturbations import perturbations

app = Flask(__name__)
for key, val in dotenv_values().items():
    app.config[key] = val
db.init_app(app)
app.cli.add_command(load_db)
app.cli.add_command(gen_sitemaps)

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
    article = Article.query.filter_by(title=Article.unperturb(unquote(title), perturbation)).first()
    if not article:
        abort(404)
    article.perturb(perturbation)
    return render_template('article.html', article=article)

@app.route('/robots.txt')
@app.route('/robots.txt', subdomain="<perturbation>")
def robots(perturbation=None):
    return render_template('robots.txt', perturbation=perturbation)

@app.route('/sitemap.xml')
@app.route('/sitemap.xml', subdomain="<perturbation>")
def sitemap(perturbation=''):
    return send_from_directory('static/sitemaps', perturbation, 'sitemap.xml')

@app.route('/sitemaps/<sitemap>')
@app.route('/sitemaps/<sitemap>', subdomain="<perturbation>")
def sitemaps(sitemap, perturbation=''):
    return send_from_directory('static/sitemaps', perturbation, sitemap)