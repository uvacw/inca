'''
This file contains the basics to determine the overlap based on cosine similarity
'''

from ..core.analysis_base_class import Analysis
import datetime 
from collections import defaultdict
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
from ..core.database import client, elastic_index, scroll_query
import os
import logging
from sys import maxunicode
import unicodedata
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import numpy as np
import gensim
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.models import Word2Vec
from gensim.similarities import SoftCosineSimilarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

logger = logging.getLogger("INCA")

class softcosine_similarity(Analysis):
    '''Compares documents from source and target, showing their softcosine distance'''
    
    def date_comparison(self, first_date, second_date):
        if first_date is None or second_date is None:
            return("No date")
        else:
            try:       # assume datetime objects
                difference = (first_date-second_date).days
            except:    # handle strings
                first = [int(i) for i in first_date[:10].split("-")]
                first = datetime.date(first[0], first[1], first[2])
                second = [int(i) for i in second_date[:10].split("-")]
                second = datetime.date(second[0], second[1], second[2])
                difference = (first-second).days
            return([first, second, difference])
        
    def fit(self, path_to_model, source, sourcetext, sourcedate, target, targettext, targetdate, days_before = None, days_after = None, threshold = None, from_time=None, to_time=None, to_csv = False):
        '''
        Model = Supply a pre-trained word2vec model. Information on how to train such a model can be found here:https://rare-technologies.com/word2vec-tutorial/ Alternatively, you can also use the pre-trained model at:...
        Source = doctype of source, Sourcetext = field of sourcetext (e.g. 'text'), 
        Sourcedate = field of sourcedate (e.g. 'publication_date'); (repeat for target); 
        Days_before = days target is before source (e.g. -2); Days_after = days target is after source (e.g. 2)
        threshold = threshold to determine at which point similarity is sufficient
        from_time, to_time = optional: specifying a date range to filter source and target articles
        to_csv = if True save the resulting data in a csv file - otherwise a pandas dataframe is returned
        '''
        logger.info("The results of the similarity analysis could be inflated when not using the recommended text processing steps (stopword removal, punctuation removal, stemming) beforehand")

        softcosine_model = gensim.models.Word2Vec.load(path_to_model)
        
        source_query = {'query':{'bool':{'filter':[{'term':{'_type':source}}]}}}
        target_query = {'query':{'bool':{'filter':[{'term':{'_type':target}}]}}}

        #Change query if date range was specified
        
        source_range = {'range':{sourcedate:{}}}
        target_range = {'range':{targetdate:{}}}
        if from_time :
            source_range['range'][sourcedate].update({ 'gte' : from_time })
            target_range['range'][targetdate].update({ 'gte' : from_time })
        if to_time:
            source_range['range'][sourcedate].update({ 'lte' : to_time   })
            target_range['range'][targetdate].update({ 'lte' : to_time   })
        if from_time or to_time:
            source_query['query']['bool']['filter'].append(source_range)
            target_query['query']['bool']['filter'].append(target_range)
        source_query = scroll_query(source_query)
        target_query = scroll_query(target_query)
        corpus = [a for a in target_query]
        ids = [a['_id'] for a in corpus]
        texts = [a['_source'][targettext].split() for a in corpus]
        dictionary = Dictionary(texts)
        tfidf = TfidfModel(dictionary=dictionary)
        similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)
        index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in texts]],similarity_matrix)
        source_query = [a for a in source_query]
        query_ids = [a['_id'] for a in source_query]
        query_generator = [tfidf[dictionary.doc2bow(n['_source'][sourcetext].split())] for n in source_query]
        query_generator = (item for item in query_generator)
        sims_list = [index[doc] for doc in query_generator]

            

        
        
        #Retrieve documents and process them
        
        
    




