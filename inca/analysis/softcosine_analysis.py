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
import time

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
        
    def fit(self, path_to_model, source, sourcetext, sourcedate, target, targettext, targetdate, days_before = None, days_after = None, threshold = None, from_time=None, to_time=None, to_csv = False, destination='exports/'):
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

        #Load the pretrained model
        softcosine_model = gensim.models.Word2Vec.load(path_to_model)

        #Construct query for elasticsearch
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

        #Retrieve source and target articles as generators
        source_query = scroll_query(source_query)
        target_query = scroll_query(target_query)

        #Make generators into lists
        corpus = [a for a in target_query if targettext in a['_source'].keys() and targetdate in a['_source'].keys()]
        source_query = [a for a in source_query if sourcetext in a['_source'].keys() and sourcedate in a['_source'].keys()]

        #If specified, calculate day difference
        source_tuple = []
        target_tuple = []
        if days_before != None or days_after != None:
            for doc in source_query:
                source_tuple.append((doc['_source'][sourcetext], doc['_source'][sourcedate], doc['_id']))
            for doc in corpus:
                target_tuple.append((doc['_source'][targettext], doc['_source'][targetdate], doc['_id']))
                    
            #Make a dict that stores as key how many days apart two documents are and their texts as tuple
            corpus_new = []
            corpus_final = []
            dates_new = []
            dates_final = []
            ids_new = []
            ids_final = []
                             
            for sourcetd in source_tuple:
                for targettd in target_tuple:
                    day_diff = self.date_comparison(sourcetd[1], targettd[1])
                    if day_diff == "No date" or days_after <= day_diff[2] <= days_before:
                        pass
                    else:
                        corpus_new.append(targettd[0])
                        dates_new.append(targettd[1])
                        ids_new.append(targettd[2])
                corpus_final.append(corpus_new)
                dates_final.append(dates_new)
                ids_final.append(ids_new)

            source_dates = [doc['_source'][sourcedate] for doc in source_query]
        
            #Make corpus IDs and texts
            texts_split = []
            for text in corpus_final:
                texts = [a.split() for a in text]
                texts_split.append(texts)
            #Make a similarity matrix and index out of the texts in the corpus (what the source articles will be compared to)
            index_lists = []
            for text in texts_split:
                dictionary = Dictionary(text)
                tfidf = TfidfModel(dictionary=dictionary)
                similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)
                index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in text]],similarity_matrix)
                index_lists.append(index)
            #Retrieve source IDs and make generator to compute similarities between each source and the index
            source_ids = [a['_id'] for a in source_query]
            query_generator = [tfidf[dictionary.doc2bow(n['_source'][sourcetext].split())] for n in source_query]
            source_index = list(zip(query_generator, index_lists))
            #Retrieve similarities and make dataframe
            for i in source_index:
                print(i[1][i[0]])
            sims_list = [item[1][item[0]] for item in source_index]
            #df = pd.DataFrame(sims_list, columns=target_ids, index = source_ids)
            #df2 = df.stack()

            #Optional: save as csv file
            #if to_csv == True:
              #  now = time.localtime()
              #  df2.to_csv(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.csv".format(now=now, target = target, source = source)))

           # else:
              #  now = time.localtime()
              #  df2.to_pickle(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.pkl".format(now=now, target = target, source = source)))
        
        #keyerror text
        #day differences
        #in dataset: dates of both articles + daydiff + doctype + threshold?
 #-----------------------------------------------------------------------------------------------------------------------------------------------       
        
    #target_ids = [a['_id'] for a in corpus]
            #texts = [a['_source'][targettext].split() for a in corpus]

            #Make a similarity matrix and index out of the texts in the corpus (what the source articles will be compared to)
            #dictionary = Dictionary(texts)
            #tfidf = TfidfModel(dictionary=dictionary)
            #similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)
            #index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in texts]],similarity_matrix)

            #Retrieve source IDs and make generator to compute similarities between each source and the index
            #source_ids = [a['_id'] for a in source_query]
            #query_generator = [tfidf[dictionary.doc2bow(n['_source'][sourcetext].split())] for n in source_query]
            #query_generator = (item for item in query_generator)

            #Retrieve similarities and make dataframe
           # sims_list = [index[doc] for doc in query_generator]
            #df = pd.DataFrame(sims_list, columns=target_ids, index = source_ids)
            #df2 = df.stack()

            #Optional: save as csv file
            #if to_csv == True:
                #now = time.localtime()
                #df2.to_csv(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.csv".format(now=now, target = target, source = source)))

            #else:
                #now = time.localtime()
                #df2.to_pickle(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.pkl".format(now=now, target = target, source = source)))
        




