'''

This file contains the class for processor scripts. Processors
should take a document id list or iterable as input and add a new key:value pair (with
corresponding metadata).

the <function>_processing class should have a `process` method that
yields a key:value pair per document, but does not need to return the old document
(the old document will simple be expanded).   

''' 

import logging
from core.document_class import Document
from core.database import get_document, update_document, check_exists

logger = logging.getLogger(__name__)

class Processer(Document):
    '''
    Processors change individual documents, for example by tokenizing, lemmatizing
    parsing XML sources etcetera. 
    
    Make processers in the 'processers' folder by using <datasource>_processer.py as 
    the filename, containing a class which inherits from this class. 
    
    '''

    functiontype = 'processing'

    def __init__(self, test=True, async=True):
        '''Override test to save results and return an ID list instead of updated documents'''
        self.test  = test
        self.async = async

    def _test_function(self):
        '''OVERWRITE THIS METHOD, should yield True (if it works) or False (if it doesn't) '''
        return {self.__name__ : {'status':False, 'message':'UNKNOWN' }}
        
    def process(self, document_field, *args, **kwargs):
        '''CHANGE THIS METHOD, should return the changed document'''
        return updated_field

    def run(self, document,field ,save=False, force=False, *args, **kwargs):
        # 1. check if document or id --> return doc
        if not (type(document)==dict and '_source' in document.keys()):
            if check_exists(document):
                document = get_document(document)
            else:
                logger.debug("document retrieval failure {document}".format(**locals()))
                return {}
            
        # 2. check whether processing can be skipped
        new_key =  "%s_%s" %(field, self.__name__)
        if not force and new_key in document['_source'].keys(): return document
        # 3. return None if key is missing
        if not field in document['_source'].keys():
            print(document['_source'].keys())
            raise "OMG WTF BBQ"
            return None
        # 4. process document
        document['_source'][new_key] = self.process(document['_source'][field], *args, **kwargs)
        # 3. add metadata
        document['_source']['META'][new_key] = self.process.__doc__
        # 4. check metadata
        self._verify(document['_source'])
        # 5. save if requested
        if save: update_document(document, force=force)
        # 6. emit dotkey-field
        return document
