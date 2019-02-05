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
            days_after = None, merge_weekend = False, threshold = None, from_time=None, to_time=None, to_csv = False, destination='comparisons', to_pajek = False):
        '''
        path_to_model = Supply a pre-trained word2vec model. Information on how to train such a model
        can be found here: https://rare-technologies.com/word2vec-tutorial/
        source/target = doctype of source/target (can also be a list of multiple doctypes)

        sourcetext/targettext = field where text of target/source can be found (defaults to 'text')
        sourcdate/targetedate = field where date of source/target can be found (defaults to 'publication_date')
        keyword_source/_target = optional: specify keywords that need to be present in the textfield; list or string, in case of a list all words need to be present in the textfield (lowercase)
        condition_source/target = optional: supply the field and its value as a dict as a condition for analysis, e.g. {'topic':1} (defaults to None)
        days_before = days target is before source (e.g. 2); days_after = days target is after source (e.g. 2) -> either both or none should be supplied. Additionally, merge_weekend = True will merge articles Saturday and Sunday. 
        threshold = threshold to determine at which point similarity is sufficient; if supplied only the rows who pass it are included in the dataset
        from_time, to_time = optional: specifying a date range to filter source and target articles. Supply the date in the yyyy-MM-dd format.
        to_csv = if True save the resulting data in a csv file - otherwise a pandas dataframe is returned
        destination = optional: where should the resulting datasets be saved? (defaults to 'comparisons' folder)
        to_pajek = if True save - in addition to csv/pickle - the result (source, target and similarity score) as pajek file to be used in the Infomap method (defaults to False)
        '''
        logger.info("The results of the similarity analysis could be inflated when not using the recommended text processing steps (stopword removal, punctuation removal, stemming) beforehand")

        #Load the pretrained model (different ways depending on how the model was saved)
        try:
            softcosine_model = gensim.models.Word2Vec.load(path_to_model)
        except:
            softcosine_model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(path_to_model, binary = True)

        #Construct query for elasticsearch
        if isinstance(source, list): # if multiple doctypes are specified
            source_query = {'query':{'bool':{'filter':{'bool':{'must':[{'terms':{'doctype':source}}]}}}}} 
        elif isinstance(source, str):
            source_query = {'query':{'bool':{'filter':{'bool':{'must':[{'term':{'doctype':source}}]}}}}}

        if isinstance(target, list): # if multiple doctypes are specified
            target_query = {'query':{'bool':{'filter':{'bool':{'must':[{'terms':{'doctype':target}}]}}}}}
        elif isinstance(target, str):
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
        #print(source_query[0])

        #Target and source texts (split), and create total corpus for the similarity matrix
        target_text=[]
        for doc in target_query:
            target_text.append(doc['_source'][targettext].split())
        source_text=[]
        for doc in source_query:
            source_text.append(doc['_source'][sourcetext].split())
        corpus = source_text + target_text

        # prepare dictionary, tfidf model and similarity matrix for softcosine analysis
        dictionary = Dictionary(corpus)
        tfidf = TfidfModel(dictionary=dictionary)
        similarity_matrix = softcosine_model.wv.similarity_matrix(dictionary, tfidf)        

        
        #If specified, calculate day difference
        source_tuple = []
        target_tuple = []
        if days_before != None or days_after != None:

            # sort dicts by date
            # group information by date
            # if merge: merge Sunday or Saturday together
            # compare current date group with X days before or after group.

            # merge source_query and target_query including identifier key
            for i in source_query:
                i.update({'identifier':'source'})
            for i in target_query:
                i.update({'identifier':'target'})
            source_query.extend(target_query)

            # sourcedate and targetdate need to be the same key
            if targetdate is not sourcedate:
                logger.info('Make sure that sourcedate and targetdate are the same key.')

            else: # do everything for sourcedate
        
                # convert targetdate and sourcedate into datetime objects if not already
                for a in source_query:
                    if isinstance(a['_source'][sourcedate], datetime.date) == True:
                        pass
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
                    date_list.append([d1 + datetime.timedelta(i)])

                # create lists per date
                for date in date_list:
                    for a in source_query:
                        if a['_source'][sourcedate] == date[0]:
                            date.append(a)
                for date in date_list:
                    del date[0] # delete date from list
### POSSIBLE TO DELETE IMMEDIATELY?
                
                # split text
                #count1 = 0
                #count2 = 0
                for date in date_list:
                    for doc in date:
                        if doc['identifier'] == 'source':
                            #count1 += 1
                            doc['_source'][sourcetext] = doc['_source'][sourcetext].split()
                            #print('source:', count1)
                        elif doc['identifier'] == 'target':
                            #count2 += 1
                            doc['_source'][targettext] = doc['_source'][targettext].split()
                            #print('target:', count2)
                            #print(doc['_source'][targettext])
                
                # Optional: merges saturday and sunday into one list
                if merge_weekend == False:
                    pass
                if merge_weekend == True:
                    # if date is sunday, merge with previous group
                    pass
                
                sims_list = []
                source_ids = []
                source_dates = []
                source_doctypes = []
                target_ids = []
                target_dates = []
                target_doctypes = []
                
                len_window = days_before + days_after + 1
                for e in self.window(date_list, n = len_window):
                    # determine position of source in window tuple
                    # index position is equivalent to days_before (e.g. 2 days before, means 3rd day is the source with index position [2]
                    source_pos = days_before
                    source_texts = []
                    target_texts = []
                    for item in e[source_pos]:
                        for doc in item:
                            # do everything for source, including making index.
                        for item 

                    for index, item in enumerate(e):
                        if index == source_pos:
                            for doc in item:
                                if doc['identifier'] == 'source': # do only for the source documents
                                    #print(doc['_source'][sourcetext])
                                    source_texts.append(doc['_source'][sourcetext])
                                    # extract other information
                                    source_ids.append(doc['_id'])
                                    source_dates.append(doc['_source'][sourcedate])
                                    source_doctypes.append(doc['_source']['doctype'])
                                else:
                                    pass
                            
                        elif index != source_pos:
                            for i in index:
                            # other positions in window tuple are targets
                            if doc['identifier'] == 'target':
                                target_texts.append(doc['_source'][targettext])
                                # extract other information
                                target_ids.append(doc['_id'])
                                target_dates.append(doc['_source'][targetdate])
                                target_doctypes.append(doc['_source']['doctype'])
                            else:
                                pass
                    print(len(target_texts))
                    print(len(source_texts))
                    print(len(source_ids))
                    index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in source_texts]], similarity_matrix)
                    query = tfidf[[dictionary.doc2bow(d) for d in target_texts]]
                    sims = index[query]
                    sims_list.append(sims)

                #print(len(sims_list))
                #print(len(source_ids))
                    
                # create dataframe
                df = pd.DataFrame.from_dict({'source':source_ids,
                                                 'target':target_ids,
                                                 'source_date':source_dates,
                                                 'target_date':target_dates,
                                                 'source_doctype':source_doctypes,
                                                 'target_doctype':target_doctypes,
                                                 'similarity':sims_list})
            
            #Optional: if threshold is defined
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

                # notes and weights from dataframe
                G = nx.from_pandas_edgelist(df, source='source', target='target', edge_attr='similarity')
                # write to pajek
                now = time.localtime()
                nx.write_pajek(G, os.path.join(destination, r"INCA_pajek_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.net".format(now=now, target=target, source=source)))



                
        #Same procedure as above, but without specifying a limited difference between source and target date (thus: comparing all sources to the same index)
        else:
            #extract information from sources
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

            #Create index out of target texts
            index = SoftCosineSimilarity(tfidf[[dictionary.doc2bow(d) for d in target_text]],similarity_matrix)

            #Retrieve source IDs and make generator to compute similarities between each source and the index
            source_ids = [a['_id'] for a in source_query]
            query = tfidf[[dictionary.doc2bow(d) for d in source_text]]
            query_generator = (item for item in query)
                            
            #Retrieve similarities
            sims_list = [index[doc] for doc in query_generator]

            #make dataframe
            df = pd.DataFrame(sims_list, columns=target_ids, index = source_ids).stack().reset_index()
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

                # notes and weights from dataframe
                G = nx.from_pandas_edgelist(df, source='source', target='target', edge_attr='similarity')
                # write to pajek
                now = time.localtime()
                nx.write_pajek(G, os.path.join(destination, r"INCA_softcosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.net".format(now=now, target=target, source=source)))

            # include_monday without days_before/days_after
            if include_monday == True:
                logger.info('Include_monday is specified without days_before/days_after and will be ingnored.')
        
    def predict(self, *args, **kwargs):
        pass

    def quality(self, *args, **kwargs):
        pass

    def interpretation(self, *args, **kwargs):
        pass

