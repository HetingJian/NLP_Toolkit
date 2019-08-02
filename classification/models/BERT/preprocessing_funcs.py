# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 10:44:05 2019

@author: WT
"""
import os
import pickle
import pandas as pd
from pytorch_pretrained_bert import BertTokenizer
import logging

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', \
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger(__file__)

def load_pickle(filename):
    completeName = os.path.join("./data/",\
                                filename)
    with open(completeName, 'rb') as pkl_file:
        data = pickle.load(pkl_file)
    return data

def save_as_pickle(filename, data):
    completeName = os.path.join("./data/",\
                                filename)
    with open(completeName, 'wb') as output:
        pickle.dump(data, output)
        
### remove stopwords and non-words from tokens list
def filter_tokens(tokens, stopwords):
    tokens1 = []
    for token in tokens:
        token = token.lower()
        if (token not in stopwords) and (token not in [".",",",";","&","'s", ":", "?", "!","(",")",\
            "'","'m","'no","***","--","...","[","]"]):
            tokens1.append(token)
    return tokens1

def dummy_fun(doc):
    return doc

def preprocess(args):
    logger.info("Preprocessing data...")
    df_train = pd.read_csv(args.train_data)
    df_test = pd.read_csv(args.infer_data)
    
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokens_length = 300 # max tokens length
    
    logger.info("Tokenizing data...")
    ### tokenize data for BERT
    df_train.loc[:, "text"] = df_train["text"].apply(lambda x: tokenizer.tokenize("[CLS] " + x))
    df_train.loc[:, "text"] = df_train["text"].apply(lambda x: tokenizer.convert_tokens_to_ids(x[:(tokens_length-1)] + ["[SEP]"]))
    df_test.loc[:, "text"] = df_test["text"].apply(lambda x: tokenizer.tokenize("[CLS] " + x))
    df_test.loc[:, "text"] = df_test["text"].apply(lambda x: tokenizer.convert_tokens_to_ids(x[:(tokens_length-1)] + ["[SEP]"]))
    
    ### fill up reviews with [PAD] if word length less than tokens_length
    def filler(x, pad=0, length=tokens_length):
        dum = x
        while (len(dum) < length):
            dum.append(pad)
        return dum
    
    logger.info("Padding sequences...")
    df_train.loc[:, "text"] = df_train["text"].apply(lambda x: filler(x))
    df_test.loc[:, "text"] = df_test["text"].apply(lambda x: filler(x))
    df_train[:, "fills"] = df_train["text"].apply(lambda x: x.count(0))
    df_test[:, "fills"] = df_test["text"].apply(lambda x: x.count(0))
    
    logger.info("Saving..")
    df_train.to_pickle(os.path.join("./data/", "train_processed.pkl"))
    df_test.to_pickle(os.path.join("./data/", "infer_processed.pkl"))
    logger.info("Done!")
    