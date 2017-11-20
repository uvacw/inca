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
        
    def text_processing(self, text, language):
                                    
        doc = text.replace(u"`",u"").replace(u"´",u"").translate(tbl)
        stopwords_list = set(stopwords.words(language))
        doc1 = " ".join([w for w in doc.split() if w not in stopwords_list])
        stemmer = SnowballStemmer(language)
        doc2 = " ".join([stemmer.stem(w) for w in doc1.split()])
        return doc2
                            
                            
    def analysis(self, source, sourcetext, sourcedate, target, targettext, targetdate, days_before = 0, days_after = 2, language = "dutch", threshold = 0.6,from_time=None, to_time=None):
        '''
        Source = doctype of source, Sourcetext = field of sourcetext (e.g. 'text'), 
        Sourcedate = field of sourcedate (e.g. 'publication_date'); (repeat for target); 
        Days_before = days target is before source (e.g. -2); Days_after = days target is after source (e.g. 2)
        Language = language used for text processing
        threshold = threshold to determine at which point similarity is sufficient
        from_time, to_time = optional: specifying a date range to filter source and target articles
        '''
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
            source_new = self.text_processing(doc['_source'][sourcetext], language)
            source_tuple.append((source_new, doc['_source'][sourcedate]))
            allsource +=1
        for doc in target_query:
            target_new = self.text_processing(doc['_source'][targettext], language)
            target_tuple.append((target_new, doc['_source'][targetdate]))
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
                    source_new = self.text_processing(item[0], language)
                    target_new = self.text_processing(item1[0], language)
                    comparisons[day_diff[2]].append((source_new, target_new, day_diff[0], day_diff[1]))
                    
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
                    for i,j,v in zip(cx.row, cx.col, cx.data):
                        if len(cx.data) == 2:
                            overlap[key1].append("no")
                            overlap[key1].append(0)
                        else: 
                            if v > threshold and i == 0 and j == 1:
                                overlap[key1].append("yes")
                                overlap[key1].append(v)                       
                            elif v <= threshold and i == 0 and j ==1:
                                overlap[key1].append("no")
                                overlap[key1].append(v)

        for key, value in int_allarticles.items():
            logger.debug("With {} days between the documents: Compared {} documents pairs".format(key, value))

        #Make a folder where all the information is stored in a csv file - can then be used for further analysis
        
        if not 'comparisons' in os.listdir('.'):
            os.mkdir('comparisons')
        with open(os.path.join('comparisons',"{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))),'w') as f:
            writer=csv.writer(f)
            headerrow = ["source_date", "day_diff", "source", "target", "made threshold", "similarity"]
            writer.writerow(headerrow)
            for key, value  in overlap.items():
                row = [value[0], value[1], value[2], value[3], value[4], value[5]]
                writer.writerow(row)

               
        




