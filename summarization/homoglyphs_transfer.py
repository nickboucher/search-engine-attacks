import pandas as pd
from transformers import pipeline
import torch
import json
import random

from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

random.seed(123)

import warnings
warnings.filterwarnings("ignore")

def load_vocabulary():
    path = "./tmp/dict.json"

    #load the vocabulary
    with open(path, 'r') as file:
        c2h = json.load(file)
        file.close()

    return c2h

def sanitize(x):
        x = list(x)
        x = [xx if xx not in h2c.keys() else h2c[xx] for xx in x]
        x = ''.join(x)
        return x

def run_summarization(model, batch):
    #forward the model
    x = model(batch, truncation=True, do_sample=False)

    #unpack the results
    x = [sanitize(xx['summary_text']) for xx in x]
    return x

def score_function(y_true_summ, y_adv_summ):
    #empty vector containing the results
    res = []

    for xx, yy in zip(y_true_summ, y_adv_summ):
        # print(y_true_summ, "\n" ,cand, "\n\n\n")
        score = sentence_bleu([xx.split()], yy.split(), smoothing_function=SmoothingFunction().method1)
        res.append(score)

    return res

if __name__ == '__main__':
    #define the log
    log_df = pd.DataFrame(None, columns = ["Model", "#sample", "y_true_summ", "y_adv_summ" ,"score"])

    #define the folder
    attack = "omoglyphs"
    folder = f"transferability/{attack}/"

    #load the vocablary for the sanitization
    global c2h
    c2h = load_vocabulary()
    global h2c
    h2c = {}

    for k, v in c2h.items():
        h2c[v] = k

    #load the data
    corpus = []
    for i in range(500):
        with open(f"./results/{attack}/{i}.json", "r") as file:
            corpus.append(json.load(file))
            file.close()
    #
    # corpus = corpus[:3]

    X_true = [x['x_true'] for x in corpus]
    X_adv = [x['x_adv'] for x in corpus]
    #
    # print(type(X_true[0]))
    # print(type(X_true[1]))
    # print(type(X_true[2]))

    ### ------------------------- model -------------------------------------
    model_name = "facebook/bart-large-cnn"
    # model_name = "google/roberta2roberta_L-24_cnn_daily_mail"
    summarizer = pipeline("summarization", model=model_name, device = 0)

    #obtain the summarization
    y_true_summ = run_summarization(summarizer, X_true)
    y_adv_summ = run_summarization(summarizer, X_adv)
    score = score_function(y_true_summ, y_adv_summ)

    #update the log
    for i, (xx, yy, zz) in enumerate(zip(y_true_summ, y_adv_summ, score)):
        log_df.loc[len(log_df)] = [model_name, i, xx, yy, zz]

    log_df.to_csv(f'{folder}results.csv')

    ### ------------------------- model -------------------------------------
    model_name = "sshleifer/distilbart-cnn-12-6"
    summarizer = pipeline("summarization", model=model_name, device = 0)

    #obtain the summarization
    y_true_summ = run_summarization(summarizer, X_true)
    y_adv_summ = run_summarization(summarizer, X_adv)
    score = score_function(y_true_summ, y_adv_summ)

    #update the log
    for i, (xx, yy, zz) in enumerate(zip(y_true_summ, y_adv_summ, score)):
        log_df.loc[len(log_df)] = [model_name, i, xx, yy, zz]

    log_df.to_csv(f'{folder}results.csv')

    ### ------------------------- model -------------------------------------
    model_name = "sshleifer/distilbart-xsum-12-6"
    summarizer = pipeline("summarization", model=model_name, device = 0)

    #obtain the summarization
    y_true_summ = run_summarization(summarizer, X_true)
    y_adv_summ = run_summarization(summarizer, X_adv)
    score = score_function(y_true_summ, y_adv_summ)

    #update the log
    for i, (xx, yy, zz) in enumerate(zip(y_true_summ, y_adv_summ, score)):
        log_df.loc[len(log_df)] = [model_name, i, xx, yy, zz]

    log_df.to_csv(f'{folder}results.csv')
