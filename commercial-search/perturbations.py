#!/usr/bin/env python3
#
# perturbations.py
# Nicholas Boucher - December 2021
# Contains perturbations available in the app.
#
from flask import abort

perturbations = ['base', 'zwsp', 'rlo']

def perturb(input: str, perturbation: str) -> str:
    match perturbation:
        case 'base' : return input
        case 'zwsp' : return '\u200b'.join(list(input))
        case 'rlo'  : return '\u2066\u202E' + input[::-1] + '\u202C\u2069'
        case _ : abort(404)

def unperturb(input: str, perturbation: str) -> str:
    match perturbation:
        case 'base' : return input
        case 'zwsp' : return input.replace('\u200b', '')
        case 'rlo'  : return input[2:-2][::-1]
        case _ : abort(404)