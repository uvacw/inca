'''
This file contains the basics to determine the overlap based on cosine similarity
'''

import datetime 
from collections import defaultdict
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
from core.database import client, elastic_index, scroll_query
import os
import logging
from sys import maxunicode
import unicodedata
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
tbl = dict.fromkeys(i for i in range(maxunicode) if unicodedata.category(chr(i)).startswith('P'))

class cosine_similarity():
    '''Compares documents from source and target, showing their cosine distance'''
    
    def date_comparison(self, first_date, second_date):
        if first_date is None or second_date is None:
            return("No date")
        else:
            first = [int(i) for i in first_date.split("-")]
            first = datetime.date(first[0], first[1], first[2])
            second = [int(i) for i in second_date.split("-")]
            second = datetime.date(second[0], second[1], second[2])
            difference = (first-second).days
            return([first, second, difference])
                            
    def levenshtein(self, source, target):
        if len(source) < len(target):
            return self.levenshtein(target, source)
        if len(target) == 0:
            return len(source)
        source = np.array(tuple(source))
        target = np.array(tuple(target))
        previous_row = np.arange(target.size + 1)
        for s in source:
            current_row = previous_row + 1
            current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))
            current_row[1:] = np.minimum(current_row[1:],
                                         current_row[0:-1] + 1)
            previous_row = current_row
            return previous_row[-1]
        
    def analysis(self, source, sourcetext, sourcedate, target, targettext, targetdate, days_before = 0, days_after = 2, threshold = 0.6, from_time=None, to_time=None, to_csv = False, method = "cosine"):
        '''
        Source = doctype of source, Sourcetext = field of sourcetext (e.g. 'text'), 
        Sourcedate = field of sourcedate (e.g. 'publication_date'); (repeat for target); 
        Days_before = days target is before source (e.g. -2); Days_after = days target is after source (e.g. 2)
        threshold = threshold to determine at which point similarity is sufficient
        from_time, to_time = optional: specifying a date range to filter source and target articles
        to_csv = if True save the resulting data in a csv file - otherwise a pandas dataframe is returned
        method = options "cosine", "levenshtein" or "both", depending on which method should be used for determining overlap
        '''
        logger.info("The results of the similarity analysis could be inflated when not using the recommended text processing steps (stopword removal, punctuation removal, stemming) beforehand")
        
        int_allarticles = defaultdict(int)
        comparisons=defaultdict(list)
        overlap = defaultdict(list)
        source_tuple = []
        target_tuple = []
        allsource = 0
        alltarget = 0

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

        #Retrieve documents and process them
        
        for doc in source_query:
            source_tuple.append((doc['_source'][sourcetext], doc['_source'][sourcedate]))
            allsource +=1
        for doc in target_query:
            target_tuple.append((doc['_source'][targettext], doc['_source'][targetdate]))
            alltarget +=1

        logger.debug("Processed {} sources in total".format(allsource))
        logger.debug("Processed {} targets in total".format(alltarget))
        
        #Make a dict that stores as key how many days apart two documents are and their texts as tuple
    
        for item in source_tuple:
            for item1 in target_tuple:
                day_diff = self.date_comparison(item[1], item1[1])
                if day_diff == "No date" or days_after <= day_diff[2] <= days_before:
                    pass
                else:
                    comparisons[day_diff[2]].append((item[0], item1[0], day_diff[0], day_diff[1]))
                    
        #For every key (documents are within 2 days) every pair of documents is evaluated with regard to their similarity
        
        for key in list(comparisons.keys()):
            if days_before <= key <= days_after:
                all_similarities = []
                documents = [list(item) for item in comparisons[key]]
                for item1 in documents:
                    key1 = item1[0]+"_"+item1[1]
                    overlap[key1].append(item1[2])
                    overlap[key1].append(key)
                    overlap[key1].append(item1[0])
                    overlap[key1].append(item1[1])
                    int_allarticles[key]+=1
                    vect = TfidfVectorizer()
                    tfidf = vect.fit_transform(item1[:2])
                    pairwise_similarity = tfidf * tfidf.T
                    cx = sp.sparse.coo_matrix(pairwise_similarity)
                    ls = self.levenshtein(item1[0], item1[1])
                    for i,j,v in zip(cx.row, cx.col, cx.data):
                        if len(cx.data) == 2:
                            if method == "levenshtein":
                                overlap[key1].append(ls)
                            elif method == "cosine": 
                                overlap[key1].append("no")
                                overlap[key1].append(0)
                            elif method == "both":
                                overlap[key1].append("no")
                                overlap[key1].append(0)
                                overlap[key1].append(ls)
                        else:
                            if v > threshold and i == 0 and j == 1:
                                if method == "levenshtein":
                                    overlap[key1].append(ls)
                                elif method == "cosine": 
                                    overlap[key1].append("yes")
                                    overlap[key1].append(v)
                                elif method == "both":
                                    overlap[key1].append("yes")
                                    overlap[key1].append(v)
                                    overlap[key1].append(ls)
                            elif v <= threshold and i == 0 and j ==1:
                                if method == "levenshtein":
                                    overlap[key1].append(ls)
                                elif method == "cosine": 
                                    overlap[key1].append("no")
                                    overlap[key1].append(v)
                                elif method == "both":
                                    overlap[key1].append("no")
                                    overlap[key1].append(v)
                                    overlap[key1].append(ls)

        for key, value in int_allarticles.items():
            logger.debug("With {} days between the documents: Compared {} documents pairs".format(key, value))

        #Make dataframe where all the information is stored
        d = []
        if method == "levenshtein": 
            for key, value in overlap.items():
                row_dict = {'source_date':value[0], 'day_diff':value[1], 'source':value[2], 'target':value[3], 'levenshtein':value[4]}
                d.append(row_dict)
            data = pd.DataFrame(d, columns = ["source_date", "day_diff", "source", "target", "levenshtein"])
            
        elif method == "cosine":
            for key, value in overlap.items():
                row_dict = {'source_date':value[0], 'day_diff':value[1], 'source':value[2], 'target':value[3], 'made_threshold':value[4], 'cosine':value[5]}
                d.append(row_dict)
            data = pd.DataFrame(d, columns = ["source_date", "day_diff", "source", "target", "made_threshold", "cosine"])
            
        elif method == "both":
            for key, value in overlap.items():
                row_dict = {'source_date':value[0], 'day_diff':value[1], 'source':value[2], 'target':value[3], 'made_threshold':value[4], 'cosine':value[5], 'levenshtein': value[6]}
                d.append(row_dict)
            data = pd.DataFrame(d, columns = ["source_date", "day_diff", "source", "target", "made_threshold", "cosine", "levenshtein"])
            
        if to_csv == True:
            if not 'comparisons' in os.listdir('.'):
                os.mkdir('comparisons')
            data.to_csv(os.path.join('comparisons',"{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))),index = False, header = True)
            return "Saved file {}.csv to comparisons folder".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

        else:
            return data
                
            

               
        




