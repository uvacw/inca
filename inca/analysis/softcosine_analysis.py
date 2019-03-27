'''
This file contains the basics to determine the overlap based on softcosine similarity
'''
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from ..core.analysis_base_class import Analysis
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
import time
import networkx as nx
from itertools import groupby, islice
from collections import defaultdict, OrderedDict # is this one still neccessary?
from tqdm import tqdm



logger = logging.getLogger("INCA")

class softcosine_similarity(Analysis):
    '''Compares documents from source and target, showing their softcosine distance'''

    ## TO DO -- ALSO MAKE THIS WORK IN THE BEGINNING OF THE SEQUENCE. 
    def window2(self, seq, n):
        for i in range(len(seq)):
            yield seq[i:i+n]
            
    def window(self, seq, n):
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result

    def fit(self, path_to_model, source, target, sourcetext = 'text', sourcedate = 'publication_date',
            targettext = 'text', targetdate = 'publication_date', keyword_source = None, keyword_target = None, condition_source = None, condition_target = None, days_before = None,
            days_after = None, merge_weekend = False, threshold = None, from_time=None, to_time=None, to_csv = False, destination='comparisons', to_pajek = False, filter_above=0.5, filter_below=5):
        '''
        path_to_model = Supply a pre-trained word2vec model. Information on how to train such a model
        can be found here: https://rare-technologies.com/word2vec-tutorial/
        source/target = doctype of source/target (can also be a list of multiple doctypes)

        sourcetext/targettext = field where text of target/source can be found (defaults to 'text')
        sourcdate/targetedate = field where date of source/target can be found (defaults to 'publication_date')
        keyword_source/_target = optional: specify keywords that need to be present in the textfield; list or string, in case of a list all words need to be present in the textfield (lowercase)
        condition_source/target = optional: supply the field and its value as a dict as a condition for analysis, e.g. {'topic':1} (defaults to None)
        days_before = days target is before source (e.g. 2); days_after = days target is after source (e.g. 2) -> either both or none should be supplied. Additionally, merge_weekend = True will merge articles published on Saturday and Sunday. 
        threshold = threshold to determine at which point similarity is sufficient; if supplied only the rows who pass it are included in the dataset
        from_time, to_time = optional: specifying a date range to filter source and target articles. Supply the date in the yyyy-MM-dd format.
        to_csv = if True save the resulting data in a csv file - otherwise a pandas dataframe is returned
        destination = optional: where should the resulting datasets be saved? (defaults to 'comparisons' folder)
        to_pajek = if True save - in addition to csv/pickle - the result (source, target and similarity score) as pajek file to be used in the Infomap method (defaults to False)
        filter_above = Words occuring in more than this fraction of all documents will be filtered
        filter_below = Words occuring in less than this absolute number of docments will be filtered
        '''
        logger.info("The results of the similarity analysis could be inflated when not using the recommended text processing steps (stopword removal, punctuation removal, stemming) beforehand")

        #Load the pretrained model (different ways depending on how the model was saved)
        logger.info('Loading word embeddings...')
        try:
            softcosine_model = gensim.models.Word2Vec.load(path_to_model)
        except:
            softcosine_model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(path_to_model, binary = True)

        logger.info('Done')
        
        #Construct source and target queries for elasticsearch
        if isinstance(source, list): # multiple doctypes
            source_query = {'query':{'bool':{'filter':{'bool':{'must':[{'terms':{'doctype':source}}]}}}}} 
        elif isinstance(source, str): # one doctype
            source_query = {'query':{'bool':{'filter':{'bool':{'must':[{'term':{'doctype':source}}]}}}}}

        if isinstance(target, list): # multiple doctypes
            target_query = {'query':{'bool':{'filter':{'bool':{'must':[{'terms':{'doctype':target}}]}}}}}
        elif isinstance(target, str): # one doctype
            target_query = {'query':{'bool':{'filter':{'bool':{'must':[{'term':{'doctype':target}}]}}}}}

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
            source_query['query']['bool']['filter']['bool']['must'].append(source_range)
            target_query['query']['bool']['filter']['bool']['must'].append(target_range)

        #Change query if keywords were specified
        if isinstance(keyword_source, str) == True:
            source_query['query']['bool']['filter']['bool']['must'].append({'term':{sourcetext:keyword_source}})
        elif isinstance(keyword_source, list) == True:
            for item in keyword_source:
                source_query['query']['bool']['filter']['bool']['must'].append({'term':{sourcetext:item}})
        if isinstance(keyword_target, str) == True:
            target_query['query']['bool']['filter']['bool']['must'].append({'term':{targettext:keyword_target}})
        elif isinstance(keyword_target, list) == True:
            for item in keyword_target:
                target_query['query']['bool']['filter']['bool']['must'].append({'term':{targettext:item}})

        #Change query if condition_target or condition_source is specified
        if isinstance(condition_target, dict) == True:
            target_query['query']['bool']['filter']['bool']['must'].append({'match':condition_target})
        if isinstance(condition_source, dict) == True:
            source_query['query']['bool']['filter']['bool']['must'].append({'match':condition_source})

        #Retrieve source and target articles as generators
        source_query = scroll_query(source_query)
        target_query = scroll_query(target_query)

        #Make generators into lists and filter out those who do not have the specified keys (preventing KeyError)
        target_query = [a for a in target_query if targettext in a['_source'].keys() and targetdate in a['_source'].keys()]
        source_query = [a for a in source_query if sourcetext in a['_source'].keys() and sourcedate in a['_source'].keys()]

        #Target and source texts (split), and create total corpus for the similarity matrix
        target_text=[]
        for doc in target_query:
            target_text.append(doc['_source'][targettext].split())
        source_text=[]
        for doc in source_query:
            source_text.append(doc['_source'][sourcetext].split())
        corpus = source_text + target_text

        logger.info('Preparing dictionary')
        dictionary = Dictionary(corpus)
        logger.info('Removing all tokens that occur in less than {} documents or in more than {:.1f}\% or all documents from dictionary'.format(filter_below,filter_above*100))
        dictionary.filter_extremes(no_below=filter_below, no_above=filter_above)
        logger.info('Preparing tfidf model')
        tfidf = TfidfModel(dictionary=dictionary)
        logger.info('Preparing soft cosine similarity matrix')
        similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)        

        #extract additional information from sources
        source_dates = [doc['_source'][sourcedate] for doc in source_query]
        source_ids = [doc['_id'] for doc in source_query]
        source_doctype = [doc['_source']['doctype'] for doc in source_query]
        source_dict = dict(zip(source_ids, source_dates))
        source_dict2 = dict(zip(source_ids, source_doctype))

        #extract information from targets
        target_ids = [doc['_id'] for doc in target_query]
        target_dates = [doc['_source'][targetdate] for doc in target_query]
        target_dict = dict(zip(target_ids, target_dates))
        target_doctype=[doc['_source']['doctype'] for doc in target_query]
        target_dict2 = dict(zip(target_ids, target_doctype))
        
        #If specified, comparisons compare docs within sliding date window
        if days_before != None or days_after != None:
            logger.info('Performing sliding window comparisons...')
            # merge queries including identifier key
            for i in source_query:
                i.update({'identifier':'source'})
            for i in target_query:
                i.update({'identifier':'target'})
            source_query.extend(target_query)

            # sourcedate and targetdate need to be the same key (bc everything is done for sourcedate)
            if targetdate is not sourcedate:
                logger.info('Make sure that sourcedate and targetdate are the same key.')

            else:
                # convert dates into datetime objects
                for a in source_query:
                    if isinstance(a['_source'][sourcedate], datetime.date) == True:
                        pass # is already datetime object
                    else:
                        a['_source'][sourcedate]=[int(i) for i in a['_source'][sourcedate][:10].split("-")]
                        a['_source'][sourcedate] = datetime.date(a['_source'][sourcedate][0],a['_source'][sourcedate][1], a['_source'][sourcedate][2])
             
                # sort query by date
                source_query.sort(key = lambda item:item['_source'][sourcedate])

                # create list of all possible dates
                d1 = source_query[0]['_source'][sourcedate]
                d2 = source_query[-1]['_source'][sourcedate]
                delta = d2 - d1
                date_list = []
                for i in range(delta.days + 1):
                    date_list.append(d1 + datetime.timedelta(i))
                    
                # create list of docs grouped by date (dates without docs are empty lists)
                grouped_query = []
                for d in date_list:
                    dt = []
                    for a in source_query:
                        if a['_source'][sourcedate] == d:
                            dt.append(a)
                    grouped_query.append(dt)

                #### ------ TO DO: CHECK WHETHER THIS WORKS! 
                # Optional: merges saturday and sunday into one weekend group
                # Checks whether group is Sunday, then merge together with previous (saturday) group.
                if merge_weekend == False:
                    pass
                if merge_weekend == True:
                    grouped_query_new = []
                    for group in grouped_query:
                        # if group is sunday, extend previous (saturday) list, except when it is the first day in the data.
                        if group[0]['_source'][sourcedate].weekday() == 6:
                            if not grouped_query_new:
                                grouped_query_new.append(group)
                            else:
                                grouped_query_new.extend(group)
                        # if empty, append empty list
                        elif not group:
                            grouped_query_new.append([])
                        # for all other weekdays, append new list
                        else:
                            grouped_query_new.append(group)
                    grouped_query = grouped_query_new

                
                ### SLIDING WINDOW SIMILARITY PART STARTS HERE.
                # How it works:
                # A sliding window cuts the documents into groups that should be compared to each other based on their publication dates. A list of source documents published on the reference date is created. For each of the target dates in the window, the source list is compared to the targets, the information is put in a dataframe, and the dataframe is added to a list. This process is repeated for each window. We end up with a list of dataframes, which are eventually merged together into one dataframe.


                
                len_window = days_before + days_after + 1
                source_pos = days_before # source position is equivalent to days_before (e.g. 2 days before, means 3rd day is source with the index position [2])

                df_list = []

                ## TEST SOURCE_POS!
                #source_pos=0

                for e in tqdm(self.window(grouped_query, n = len_window)):
                    source_texts = []
                    source_ids = []
                    
                    if not e[source_pos]:
                        ## TO DO ------ DO THIS FOR ONLY IDENTIFIER == SOURCE
                        # if query does not include source articles published on this date, go to next window
                        ## TO DO ------ DO NOT CREATE LISTS OF TEXTS; THIS TAKES TOO LONG.
                        pass
                    else:
                        print('It should do this 4 times!!')
                        for doc in e[source_pos]:
                            if doc['identifier']=='source':
                                # create sourcetext list to compare against
                                source_texts.append(doc['_source'][sourcetext].split())
                                # extract additional information
                                source_ids.append(doc['_id'])
                                
                        #print('The length of source_texts is', len(source_texts))

                        # create index of source texts
                        query = tfidf[[dictionary.doc2bow(d) for d in source_texts]]

                        # iterate through targets
                        for d in e:
                            target_texts=[]
                            target_ids = []
                            if not d: # TO DO -- EMPTY IS ONLY FOR TARGET!
                                #print('This is empty :)')
                                pass # empty list, so pass comparison
                            else:
                                print('It should do this 4 times as well!!!')
                                for doc in d:
                                    if doc['identifier'] == 'target':
                                        target_texts.append(doc['_source'][targettext].split())
                                        # extract additional information
                                        target_ids.append(doc['_id'])
                                # do comparison
                                index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in target_texts]], similarity_matrix)
                                sims = index[query]
                                #make dataframe
                                df_temp = pd.DataFrame(sims, columns=target_ids, index = source_ids).stack().reset_index()
                                df_list.append(df_temp)
                                #print(df_temp)
                #print('This is the last df_temp that was made:', df_temp)
                print('The length of df_list is now:', len(df_list))
                
                # make total dataframe
                df = pd.concat(df_list, ignore_index=True)
                df.columns = ['source', 'target', 'similarity']
                df['source_date'] = df['source'].map(source_dict)
                df['target_date'] = df['target'].map(target_dict)
                df['source_doctype'] = df['source'].map(source_dict2)
                df['target_doctype'] = df['target'].map(target_dict2)

                ## TO DO -- DO WE NEED TO DELETE DUPLICATE COMPARISONS IN THE LIST?

                
        #Same procedure as above, but without specifying a time frame (thus: comparing all sources to all targets)
        else:
            
            #Create index out of target texts
            index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in target_text]],similarity_matrix)

            #Retrieve source IDs and make generator to compute similarities between each source and the index
            query = tfidf[[dictionary.doc2bow(d) for d in source_text]]
            query_generator = (item for item in query)
                            
            #Retrieve similarities
            sims_list = [index[doc] for doc in query_generator]

            #make dataframe
            df = pd.DataFrame(sims_list, columns=target_ids, index = source_ids).stack(). reset_index()
            df.columns = ['source', 'target', 'similarity']
            df["source_date"] = df["source"].map(source_dict)
            df["target_date"] = df["target"].map(target_dict)
            df['source_doctype'] = df['source'].map(source_dict2)
            df['target_doctype'] = df['target'].map(target_dict2)

            
        #Optional: if threshold is specified
        if threshold:
            df = df.loc[df['similarity'] >= threshold]

        #Make exports folder if it does not exist yet
        if not 'comparisons' in os.listdir('.'):
            os.mkdir('comparisons')

        #Optional: save as csv file
        if to_csv == True:
            now = time.localtime()
            df.to_csv(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.csv".format(now=now, target = target, source = source)))
        #Otherwise: save as pickle file
        else:
            now = time.localtime()
            df.to_pickle(os.path.join(destination,r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.pkl".format(now=now, target = target, source = source)))

        #Optional: additionally save as pajek file
        if to_pajek == True:
            G = nx.Graph()

            # change int to str (necessary for pajek format)
            df['similarity'] = df['similarity'].apply(str)
            # change column name to 'weights' to faciliate later analysis
            df.rename({'similarity':'weight'}, axis=1, inplace=True) 
            # notes and weights from dataframe
            G = nx.from_pandas_edgelist(df, source='source', target='target', edge_attr='weight')
            # write to pajek
            now = time.localtime()
            nx.write_pajek(G, os.path.join(destination, r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.net".format(now=now, target=target, source=source)))
        
    def predict(self, *args, **kwargs):
        pass

    def quality(self, *args, **kwargs):
        pass

    def interpretation(self, *args, **kwargs):
        pass

