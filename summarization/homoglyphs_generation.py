from genericpath import exists
import homoglyphs as hg
import numpy as np
import string
import os
import random
from scipy import spatial
from transformers import pipeline
from transformers import AutoTokenizer, AutoModel
import torch
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import json
import datetime
from datasets import load_dataset

from sentence_transformers import SentenceTransformer
from nltk import word_tokenize

random.seed(123)

import warnings
# warnings.filterwarnings("ignore")

def load_vocabulary():
    path = "./tmp/dict.json"

    #check if the vocabulary exists
    if os.path.exists(path):
        #load the vocabulary
        with open(path, 'r') as file:
            c2h = json.load(file)
            file.close()
            print(c2h)
    else:
        #create a new vocabulary
        c2h = dict()

        #define the alphabet
        alph = list(string.ascii_letters) + list(string.digits) + list(string.punctuation)

        #for each character, we define its substitution
        hist = [] #history variable -- we do not insert a mapping with already used chatacters -- guarantee a unique mapping
        for c in alph:
            #candidates
            h = [x for x in hg.Homoglyphs().get_combinations(c) if x != c]

            #filter history
            h = [c for c in h if c not in hist]

            if len(h) > 0:
                c2h[c] = h[0]
                hist.append(h[0])

        with open(path, 'w') as file:
            json.dump(c2h, file)
            file.close()

    return c2h

###----define the adversarial class -----------------
class adversarial_summarizer():
    def __init__(self, model):
        """
            model: the summarizer istance.
        """
        #save the settings
        self.model = model
        self.alphabet = string.ascii_letters
        self.log_c2h = load_vocabulary()
        self.log_h2c = {}

        for k, v in self.log_c2h.items():
            self.log_h2c[v] = k

    def sanitize(self, x):
        """ Function that correctly sanitize the input"""
        x = list(x)
        x = [xx if xx not in self.log_h2c.keys() else self.log_h2c[xx] for xx in x]
        x = ''.join(x)
        return x

    def summarize(self, batch):
        """
            Given a list of sentences [batch], it returns a list of summatizations.
        """
        #forward the model
        x = self.model(batch, truncation=True, do_sample=False)

        #unpack the results
        x = [xx['summary_text'] for xx in x]

        return x

    def score_function(self, y_true_summ, batch_cand):
        #empty vector containing the results
        res = []

        # sanitize the candidates from possible unicode characters
        # that might affect the scoring function
        batch_cand = [self.sanitize(x) for x in batch_cand]

        for cand in batch_cand:
            # print(y_true_summ, "\n" ,cand, "\n\n\n")
            score = sentence_bleu([y_true_summ.split()], cand.split(), smoothing_function=SmoothingFunction().method1)
            res.append(score)

        return res

    def poison(self, x, step = 1):
        """ This function generates the maximum perturbation of a given sample"""
        x = list(x) #list of chars
        for i in range(len(x)):
            if i % step == 0:

                if x[i] in self.log_c2h.keys(): #we already have one mapping
                    c = self.log_c2h[x[i]]
                    x[i] = c

        x = ''.join(x) #from list to string
        return x

    def count_perturbations(self, sentence):
        """ Count the size of the perturbation"""
        size = len([c for c in list(sentence) if c in self.log_h2c.keys()])
        perc = (size / len(list(sentence))) * size
        return size, perc

    def get_perturbated_idx(self, sentence):
        """ return a list of perturbation indexes"""
        return [i for i, c in enumerate(list(sentence)) if c in self.log_h2c.keys()]


    def population_generation(self, starting, max_population = 5, step = 100):
        """ Given a candidate, the function generates a population derived from it.
            In this case the population is generated by sanitizing the input by N steps.
        """
        #get a list of perturbated characters indexes
        idx = self.get_perturbated_idx(starting)

        candidates = []

        #generate the candidates
        for _ in range(max_population):
            #shuffle the indexes
            random.shuffle(idx)

            #get topN items
            cand_idx = idx[:step]

            #generate the candidate
            cand = list(starting)

            #sanitize the candidate on the random characters
            for ci in cand_idx:
                # print(cand[ci])
                cand[ci] = self.log_h2c[cand[ci]]

            #save the result
            candidates.append(''.join(cand))

        return candidates

    def adversarial_generation(self, sentence, max_population = 20, step = 250, max_it = -1, min_score = .05):
        """ Main routine to generate the adversarial samples """
        #the following duplicated lines are essential to allow sentence == sanitize(x_adv)
        sentence = ' '.join(word_tokenize(sentence))
        sentence = ' '.join(word_tokenize(sentence))

        #poison the original sentence with the maximum perturbation
        poisoned_sentence = self.poison(sentence)
        print(f"Starting perturbation number: {self.count_perturbations(poisoned_sentence)}")

        #compute the ground truth
        x_cnt = self.sanitize(poisoned_sentence)
        y = self.summarize([sentence, poisoned_sentence, x_cnt])

        print("Control:\t",sentence == x_cnt)

        y_true_summ = y[0]
        y_adv_summ = y[1]
        y_adv_cnt = y[2]
        score = self.score_function(y_true_summ, [y_adv_summ]) #upper bound of the DoS attack
        score_cnt = self.score_function(y_true_summ, [y_adv_cnt])
        print(f"Starting score: {score[0]:.4f}\tCONTROL: {score_cnt[0]:.4f}")

        # print(sentence[:100])
        # print(x_cnt[:100])

        # print(y_true_summ )
        # print(y_adv_cnt )
        # print(y_true_summ == y_adv_cnt)
        # assert score_cnt[0] == 1.0


        #init the best candidate -- at the beginning it is the original sentence
        best_candidate = (poisoned_sentence, y_adv_summ, score[0])

        execute = True
        it = 0

        #get the starting time
        start = datetime.datetime.now()

        while execute:
            it += 1 #increase the steps

            if max_it > 0:
                if it == max_it:
                    execute = False

            #generate candidates
            population = self.population_generation(best_candidate[0], max_population = max_population, step = step)
            # raise Exception(self.count_perturbations(population[0]))

            #summarize the population
            population_summ = self.summarize(population)

            #scoring function
            population_score = self.score_function(y_true_summ, population_summ)

            #we now need to find the best candidate
            # we first convert the population in a list of tuple with all the info
            population_log = []
            for xx, yy, zz in zip(population, population_summ, population_score):
                population_log.append((xx, yy, zz))

            #we now order such a list ascending
            population_log.sort(key = lambda x:x[2])

            #get the best candidate
            population_best_cand = population_log[0]

            # print(f"\nIteration {it + 1} executed in:\t{end - start}")
            print(f"\t--->best candidate score: {population_best_cand[2]:.4f}")

            #check if we can improve or if we reached a local / global minimum
            if population_best_cand[2] <= min_score: #improvement
                best_candidate = population_best_cand
            else:
                execute = False

        #get the ending time
        end = datetime.datetime.now()
        print(f"\nExecuted in --- steps: {it}\ttime:\t{end - start}")
        print(f"Best candidate perturbation: {self.count_perturbations(best_candidate[0])}")
        print(best_candidate[0], "\n\n" ,best_candidate[1])

        return best_candidate, y_true_summ



if __name__ == '__main__':
    #get execution device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)

    #max size
    max_size = 500

    #load the dataset
    dataset = load_dataset('cnn_dailymail', '3.0.0', split='test')
    # print("length:", len(dataset))
    # print(dataset[0])

    ARTICLES = []
    i = 0
    while len(ARTICLES) < max_size:
        if len(dataset[i]['article']) <= 2000:
            ARTICLES.append(dataset[i]['article'])
        i+=1
    #
    # print(np.average([len(x) for x in ARTICLES]))
    # print(np.max([len(x) for x in ARTICLES]))

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device = 0)

    # define the adversarial class
    adv_process = adversarial_summarizer(model = summarizer)

    for idx, article in enumerate(ARTICLES):
        print(f"ARTICLE: {idx}\tLength: {len(article)}")

        filename = f"./results/omoglyphs/{idx}.json"

        if os.path.exists(filename):
            print("\f The file has been already generated")
        else:
            res, y_true_summ = adv_process.adversarial_generation(article)


            var = {
                'x_true': article,
                'y_true_summ': y_true_summ,
                'x_adv': res[0],
                'y_adv_summ': res[1],
                'score': res[2]
            }

            with open(filename, "w") as file:
                json.dump(var, file)
                file.close()
