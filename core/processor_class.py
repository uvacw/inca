'''

This file contains the class for processor scripts. Processors
should take a document as input and add a new key:value pair (with
corresponding metadata).

the <function>_processing class should have a `process` method that
yields a key:value pair per document, but does not need to return the old document
(the old document will simple be expanded).   

'''

import logging
import inspect 
from core.document_class import Document
from celery.contrib.methods import task_method
import ast
from core.database import client

logger = logging.getLogger(__name__)

class Processer(Document):
    '''
    Processors change individual documents, for example by tokenizing, lemmatizing
    parsing XML sources etcetera. 
    
    Make processers in the 'processers' folder by using <datasource>_processer.py as 
    the filename, containing a class which inherits from this class. 
    
    '''

    functiontype = 'processing'
        
    pass
