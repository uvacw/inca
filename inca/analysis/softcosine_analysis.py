'''
This file contains the basics to determine the overlap based on softcosine similarity
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
        
    def fit(self, path_to_model, source, sourcetext, sourcedate, target, targettext, targetdate, days_before = None, days_after = None, threshold = None, from_time=None, to_time=None, to_csv = False, destination='exports'):
        '''
        path_to_model = Supply a pre-trained word2vec model. Information on how to train such a model 
        can be found here: https://rare-technologies.com/word2vec-tutorial/ Alternatively, you can also use the pre-trained model at:...

        source = doctype of source, Sourcetext = field of sourcetext (e.g. 'text'), 
        sourcedate = field of sourcedate (e.g. 'publication_date'); (repeat for target); 
        days_before = days target is before source (e.g. -2); days_after = days target is after source (e.g. 2) -> either both or none should be supplied
        threshold = threshold to determine at which point similarity is sufficient; if supplied only the rows who pass it are included in the dataset
        from_time, to_time = optional: specifying a date range to filter source and target articles. Supply the date in the yyyy-MM-dd format.
        to_csv = if True save the resulting data in a csv file - otherwise a pandas dataframe is returned
        destination = optional: where should the resulting datasets be saved? Defaults to 'export' folder
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

        #Make generators into lists and filter out those who do not have the specified keys (preventing KeyError)
        corpus = [a for a in target_query if targettext in a['_source'].keys() and targetdate in a['_source'].keys()]
        source_query = [a for a in source_query if sourcetext in a['_source'].keys() and sourcedate in a['_source'].keys()]

        #extract information from sources (date and id)
        source_dates = [doc['_source'][sourcedate] for doc in source_query]
        source_ids = [a['_id'] for a in source_query]
        source_dict = dict(zip(source_ids, source_dates))
        
        #If specified, calculate day difference
        source_tuple = []
        target_tuple = []
        if days_before != None or days_after != None:
            for doc in source_query:
                source_tuple.append((doc['_source'][sourcetext], doc['_source'][sourcedate], doc['_id']))
            for doc in corpus:
                target_tuple.append((doc['_source'][targettext], doc['_source'][targetdate], doc['_id']))
                    
            #Calculate day difference and make a separate corpus (basis for the index the source is compared to)
            #for every source, only including target documents within the specified range; also extracting dates and ids
            corpus_final = []
            dates_final = []
            ids_final = []                
            for sourcetd in source_tuple:
                corpus_new = []
                dates_new = []
                ids_new = []
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

            #Make corpus for every source (splitting the texts)
            texts_split = []
            for text in corpus_final:
                texts = [a.split() for a in text]
                texts_split.append(texts)

            #Make a similarity matrix and index out of the texts in the corpus (what the source articles will be compared to, one for every source)
            source_texts = [n['_source'][sourcetext].split() for n in source_query]
            source_index = list(zip(texts_split, source_texts))
            sims_list = []
            
            for item in source_index:
                dictionary = Dictionary(item[0])
                tfidf = TfidfModel(dictionary=dictionary)
                similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)
                index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in item[0]]],similarity_matrix)
                
                #Process the sources so that they can be compared to the indices
                query = tfidf[dictionary.doc2bow(item[1])]

                #Retrieve similarities and make dataframe (including both ids, dates, doctypes and similarity)
                sims = index[query]
                sims_list.append(sims)
                
            target_df = pd.DataFrame(ids_final).transpose().melt().drop('variable', axis = 1)
            target_df.columns = ['target']
            target_dates = pd.DataFrame(dates_final).transpose().melt().drop('variable', axis = 1)
            target_dates.columns = ['target_date']
            source_df = pd.DataFrame(sims_list, index = source_ids).transpose().melt()
            source_df.columns = ['source', 'similarity']
            source_df["source_date"] = source_df["source"].map(source_dict)
            df = pd.concat([source_df, target_df, target_dates], axis = 1)
            df['source_doctype'] = source
            df['target_doctype'] = target
            if threshold:
                df = df.loc[df['similarity'] >= threshold]

            #Make exports folder if it does not exist yet
            if not 'exports' in os.listdir('.'):
                os.mkdir('exports')
                
            #Optional: save as csv file
            if to_csv == True:
                now = time.localtime()
                df.to_csv(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.csv".format(now=now, target = target, source = source)))

            #Otherwise: save as pandas (pickle)
            else:
                now = time.localtime()
                df.to_pickle(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.pkl".format(now=now, target = target, source = source)))
        
        #Same procedure as above, but without specifying a limited difference between source and target date (thus: comparing all sources to the same index)
        else:
            target_ids = [a['_id'] for a in corpus]
            target_dates = [a['_source'][targetdate] for a in corpus]
            target_dict = dict(zip(target_ids, target_dates))
            texts = [a['_source'][targettext].split() for a in corpus]

            #Make a similarity matrix and index out of the texts in the corpus (what the source articles will be compared to)
            dictionary = Dictionary(texts)
            tfidf = TfidfModel(dictionary=dictionary)
            similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)
            index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in texts]],similarity_matrix)

            #Retrieve source IDs and make generator to compute similarities between each source and the index
            source_ids = [a['_id'] for a in source_query]
            query = [tfidf[dictionary.doc2bow(n['_source'][sourcetext].split())] for n in source_query]
            query_generator = (item for item in query)

            #Retrieve similarities and make dataframe
            sims_list = [index[doc] for doc in query_generator]
            df = pd.DataFrame(sims_list, columns=target_ids, index = source_ids).stack().reset_index()
            df.columns = ['source', 'target', 'similarity']
            df["source_date"] = df["source"].map(source_dict)
            df["target_date"] = df["target"].map(target_dict)
            df['source_doctype'] = source
            df['target_doctype'] = target
            if threshold:
                df = df.loc[df['similarity'] >= threshold]

            #Make exports folder if it does not exist yet
            if not 'exports' in os.listdir('.'):
                os.mkdir('exports')
                
            #Optional: save as csv file
            if to_csv == True:
                now = time.localtime()
                df.to_csv(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.csv".format(now=now, target = target, source = source)))

            else:
                now = time.localtime()
                df.to_pickle(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.pkl".format(now=now, target = target, source = source)))
        
               
    def predict(self, *args, **kwargs):
        pass

    def quality(self, *args, **kwargs):
        pass

    def interpretation(self, *args, **kwargs):
        pass

 #----------------------------------------------------------------------------------------------------------------------------------------------- 
 #TODO
        #have one 'example' model stored somewhere for people to use?


