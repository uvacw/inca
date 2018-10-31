'''
This file contains a method to use a pre-trained passive aggressive classifier
'''


from ..core.analysis_base_class import Analysis
import logging
logger = logging.getLogger("INCA")


from sklearn.externals import joblib
from ..core.database import client, elastic_index, scroll_query
from ..core.database import update_document
import pandas as pd

class pa_classifier(Analysis):
     
     def predict(self, path_to_model, source, textkey): 
          '''
          This method XXXXXXX
          
          path_to_model =  supply a pre-trained Passive Aggressive classifier model
          source = supply the doctype of interest.
          textkey = field where text of the source doctype can be found (defaults to 'text'). 
          

          '''
          
          # load pre-trained classifier
          clf = joblib.load(path_to_model)

          # construct query for elasticsearch
          source_query = {'query':{'bool':{'filter':{'bool':{'must':[{'term':{'doctype':source}}]}}}}}

          # retrieve source articles as generators and make into list
          source_query = scroll_query(source_query)
          corpus = [a for a in source_query if textkey in a['_source'].keys()] # exclude docs without textkey

          # create dataframe with ID and text
          df = pd.DataFrame(columns=['id', 'text'])
          for doc in corpus:
               df = df.append({'id':doc['_id'], 'text':doc['_source'][textkey]}, ignore_index=True)

          # run classifier
          topics = clf.predict(df['text'])

          # append classification to df
          topics = pd.Series(topics)
          df['classification']=topics.values
          print(df)

          # create new field 'pa_classifier' in database
          
          
          #update_document(document, force=force)??
          
          
          


          
          return






