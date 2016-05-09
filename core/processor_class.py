'''

This file contains the class for processor scripts. Processors
should take a document as input and add a new key:value pair (with
corresponding metadata).

the <function>_processor class should have a `process` method that
returns a key:value pair, but does not need to return the old document
(the old document will simple be expanded).   

'''

import logging
from core.document_class import Document

logger = logging.getLogger(__name__)

class Processer(Document):
    '''
    Processors change individual documents, for example by tokenizing, lemmatizing
    parsing XML sources etcetera. 
    
    Make processers in the 'processers' folder by using <datasource>_processer.py as 
    the filename, containing a class which inherits from this class. 
    
    '''

    functiontype = 'processor'
        
    def process(self, document, **kwargs):
        ''' This docstring should explain how documents are transformed '''
        logger.warning("You forgot to overwrite the 'process' method of this processor!")
        yield dict()

    def _process_document(self, document, **kwargs):
        '''
        This is an internal function that calls the 'get' method and saves the 
        resulting documents. 
        '''
        self._verify(document)
        for doc in self.process(document,**kwargs):
            self._add_metadata(doc)
            self._verify(doc)
            self._save_document(doc)
            
        
