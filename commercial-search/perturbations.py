#!/usr/bin/env python3
#
# perturbations.py
# Nicholas Boucher - December 2021
# Contains perturbations available in the app.
#
from flask import abort
from homoglyphs import Homoglyphs

perturbations = ['base', 'zwsp', 'zwnj', 'zwj', 'rlo', 'bksp', 'del', 'homo']
homoglyphs = Homoglyphs()

def perturb(input: str, perturbation: str) -> str:
    match perturbation:
        case 'base' : return input
        case 'zwsp' : return '\u200B'.join(list(input))
        case 'zwnj' : return '\u200C'.join(list(input))
        case 'zwj'  : return '\u200D'.join(list(input))
        case 'rlo'  : return '\u2066\u202E' + input[::-1] + '\u202C\u2069'
        case 'bksp' : return input[:int(len(input)/2)] + 'X\u0008' + input[int(len(input)/2):]
        case 'del'  : return input[:int(len(input)/2)] + 'X\u007F' + input[int(len(input)/2):]
        case 'homo' : return ''.join(map(lambda c: (n := homoglyphs.get_combinations(c))[p if (p := n.index(c)+1) < len(n) else 0], list(input)))
        case _ : abort(404)

def unperturb(input: str, perturbation: str) -> str:
    match perturbation:
        case 'base' : return input
        case 'zwsp' : return input.replace('\u200B', '')
        case 'zwnj' : return input.replace('\u200C', '')
        case 'zwj'  : return input.replace('\u200D', '')
        case 'rlo'  : return input[2:-2][::-1]
        case 'bksp' : return input[:int((len(input)-2)/2)] + input[int((len(input)-2)/2)+2:]
        case 'del'  : return input[:int((len(input)-2)/2)] + input[int((len(input)-2)/2)+2:]
        case 'homo' : return ''.join(map(lambda c: (n := homoglyphs.get_combinations(c))[max(n.index(c)-1, 0)], list(input)))
        case _ : abort(404)