import { homoglyphs } from './homoglyphs';

export const perturbations = ['base', 'zwsp', 'zwnj', 'zwj', 'rlo', 'bksp', 'del', 'homo'];

export function perturb(input: string, perturbation: string): string {
    switch (perturbation) {
        case 'base' : return input;
        case 'zwsp' : return input.split('').join('\u200B');
        case 'zwnj' : return input.split('').join('\u200C');
        case 'zwj'  : return input.split('').join('\u200D');
        case 'rlo'  : return '\u2066\u202E' + input.split('').reverse().join('') + '\u202C\u2069';
        case 'bksp' : return input.slice(0,Math.floor(input.length/2)) + 'X\u0008' + input.slice(Math.floor(input.length/2));
        case 'del'  : return input.slice(0,Math.floor(input.length/2)) + 'X\u007F' + input.slice(Math.floor(input.length/2));
        case 'homo' : return input.split('').map(c => c in homoglyphs ? homoglyphs[c][homoglyphs[c].indexOf(c)+1] : c).join('');
        default     : throw `Perturbation ${perturbation} not found.`;
    }
}
