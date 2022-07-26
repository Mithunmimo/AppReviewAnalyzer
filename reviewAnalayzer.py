
"""
# -*- coding: utf-8 -*-

@Author : Megha Ramesh
Last edited : 25/07/2022
Program to Analyse and report mismatched ratings and review

"""

from distutils.debug import DEBUG
from time import asctime
from scipy.special import softmax
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from tqdm.notebook import tqdm
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import numpy as np
import nltk
import logging
from datetime import datetime as dt
import time

now = dt.now().strftime('%d-%m-%Y')


logging.basicConfig(level=logging.DEBUG, filename="logs/pylogs_"+now+".txt",
                    format='%(asctime)s %(message)s', filemode='a')


def initialise():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('vader_lexicon')
    # Read in data
    df = pd.read_csv("input/inputFile.csv")
    df.head()
    df = df.head(2000)
    # Run the polarity score on the entire dataset
    sia = SentimentIntensityAnalyzer()
    res = {}
    for i, row in tqdm(df.iterrows(), total=len(df)):
        text = row['Text']
        myid = row['ID']
        res[myid] = sia.polarity_scores(str(text))
    vaders = pd.DataFrame(res).T
    vaders = vaders.reset_index().rename(columns={'index': 'ID'})
    vaders = vaders.merge(df, how='left')
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    res = {}

    def polarity_scores_roberta(data):
        encoded_text = tokenizer(data, return_tensors='pt')
        output = model(**encoded_text)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        scores_dict = {
            'roberta_neg': scores[0],
            'roberta_neu': scores[1],
            'roberta_pos': scores[2]}
        return scores_dict

    for i, row in tqdm(df.iterrows(), total=len(df)):
        try:
            text = row['Text']
            myid = row['ID']
            vader_res = sia.polarity_scores(str(text))
            vader_result_rename = {}
            for key, value in vader_res.items():
                vader_result_rename[f"vader_{key}"] = value
            roberta_res = polarity_scores_roberta(text)
            both = {**vader_result_rename, **roberta_res}
            res[myid] = both
        except RuntimeError:
            logging.error(f'Broke for id{myid}')
    results_df = pd.DataFrame(res).T
    results_df = results_df.reset_index().rename(columns={'index': 'ID'})
    results_df = results_df.merge(df, how='left')
    return results_df


def mis():
    try:
        dataset = initialise()
        # if(dataset['roberta_pos'] > 0.5):
        a = dataset.query('Star==1' or 'Star==2').sort_values(
            'roberta_pos', ascending=False)['Text']
        list1 = []
        for i in a:
            list1.append(i)
        mis_df = pd.DataFrame()
        mis_df['misclassified Text'] = list1
        mis_df.to_csv("output/outputFile.csv", index=False)
        success = 200
        logging.info("App review Analyzer process Done\nOutput file generated")
    except Exception as E:
        logging.exception(E)
        success = 400
    finally:
        return success


if __name__ == '__main__':
    try:
        start = time.time()
        print(dt.now().strftime('%d-%m-%Y'))
        # print(mis())
        end = time.time()
        print(end-start)
    except Exception as err:
        logging.exception(err)
        print(err)
