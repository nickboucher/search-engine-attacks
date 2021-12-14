#!/usr/bin/env python3
#
# models.py
# Nicholas Boucher - December 2021
# Contains DB models.
#
from flask_sqlalchemy import SQLAlchemy

# Initialize db variable to avoid namespace errors
# ('db' must be imported by application later)
db = SQLAlchemy()

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)

    def __init__(self, id, title, text):
        self.id = int(id)
        self.title = title
        self.text = text

    def __repr__(self) -> str:
        return '<Article %r>' % self.title