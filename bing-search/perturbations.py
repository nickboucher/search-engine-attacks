#!/usr/bin/env python3
#
# perturbations.py
# Nicholas Boucher - December 2022
# Implements Unicode perturbations.
#
from homoglyphs import Homoglyphs
from random import randrange

perturbations = ['base', 'zwsp', 'zwnj', 'zwj', 'rlo', 'bksp', 'del', 'homo', 'zwsp2', 'homo2']
homoglyphs = Homoglyphs()
zwsp_map = {}

hg2 = {'-':'−','.':'ꓸ','0':'Ο','1':'𝟷','2':'𝟸','3':'𖼻','4':'４','5':'５','6':'Ⳓ','7':'７','8':'𐌚','9':'Ꝯ','A':'Ꭺ','B':'Β','C':'𐊢','D':'Ꭰ','E':'Ꭼ','F':'𐊇','G':'Ꮐ','H':'Η','I':'Ⅰ','J':'Ꭻ','K':'K','L':'𐐛','M':'Μ','N':'ꓠ','O':'೦','P':'Р','Q':'Ｑ','R':'𖼵','S':'Տ','T':'Ꭲ','U':'Ս','V':'ꛟ','W':'Ԝ','X':'ⵝ','Y':'Ⲩ','Z':'Ꮓ','a':'а','b':'ᖯ','c':'ϲ','d':'ⅾ','e':'е','f':'𝖿','g':'ց','h':'𝗁','i':'𝚒','j':'ј','k':'𝚔','l':'ⅼ','m':'ｍ','n':'ո','o':'𐓪','p':'р','q':'ԛ','r':'𝗋','s':'ꮪ','t':'𝗍','u':'𝗎','v':'∨','w':'ꮃ','x':'᙮','y':'𝗒','z':'ᴢ'}
hg2_rev = {v:k for k,v in hg2.items()}

def perturb(input: str, perturbation: str, title: str = '') -> str:
    match perturbation:
        case 'base' : return input
        case 'zwsp' : return '\u200B'.join(list(input))
        case 'zwnj' : return '\u200C'.join(list(input))
        case 'zwj'  : return '\u200D'.join(list(input))
        case 'rlo'  : return '\u2066\u202E' + input[::-1] + '\u202C\u2069'
        case 'bksp' : return input[:int(len(input)/2)] + 'X\u0008' + input[int(len(input)/2):]
        case 'del'  : return input[:int(len(input)/2)] + 'X\u007F' + input[int(len(input)/2):]
        case 'homo' : return ''.join(map(lambda c: (n := homoglyphs.get_combinations(c))[p if (p := n.index(c)+1) < len(n) else 0], list(input)))
        case 'zwsp2': return zwsp2(input, title)
        case 'homo2': return ''.join(map(lambda c: hg2[c] if c in hg2 else c, list(input)))
        case _ : raise NameError(f'Perturbation {perturbation} not found.')

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
        case 'zwsp2': return input.replace('\u200B', '')
        case 'homo2': return ''.join(map(lambda c: hg2_rev[c] if c in hg2_rev else c, list(input)))
        case _ : raise NameError(f'Perturbation {perturbation} not found.')

def zwsp2(input: str, title: str) -> str:
    if title in zwsp_map:
        perturbs = zwsp_map[title]
    else:
        words = title.split(' ')
        perturbs = []
        for word in words:
            for _ in range(randrange(1,max(len(word)//2,2))):
                idx = randrange(len(word)+1)
                word = word[:idx] + '\u200B'*randrange(1,6) + word[idx:]
            perturbs.append(word)
        zwsp_map[title] = perturbs
    try:
        idx = title.split(' ').index(input)
        return perturbs[idx]
    except ValueError:
        return input

def perturb_doc(doc: dict, perturbation: str) -> dict:
    title = ' '.join(map(lambda w: perturb(w, perturbation, title=doc['title']), doc['title'].split(' ')))
    body = ' '.join(map(lambda w: perturb(w, perturbation, title=doc['title']), doc['body'].split(' ')))
    return {
        'article-id': doc['article-id'],
        'title': title,
        'body': body,
    }