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
        
    def process(self, document, **kwargs):
        ''' This docstring should explain how documents are transformed '''
        logger.warning("You forgot to overwrite the 'process' method of this processor!")
        return dict()

    def run(self, function="", *args, **kwargs):
        func = getattr(self,function)
        if func=="help" or func=="?":
            return func.__doc__
        is_generator = inspect.isgeneratorfunction(func)
        if is_generator:
            for result in func(*args, **kwargs):
                yield result
        else:
            yield func(*args,**kwargs)    
        
    def _process_document(self, document, **kwargs):
        '''
        This is an internal function that calls the 'process' method and saves the 
        resulting documents. 
        '''
        self._verify(document)
        for doc in self.process(document,**kwargs):
            self._add_metadata(doc)
            self._verify(doc)
            self._save_document(doc)

    def test(self, query={"match_all":{}}, *args, **kwargs):
        '''This is a private method that previews the result of 10 documents without saving changes '''
        if type(query)==str:
            query = self._parse_strings_that_contain_dicts(query)
        query = {'size':10,'query':query}
        results = client.search(index='inca', body=query)
        docs = [doc for doc in results['hits']['hits']]
        updates = dict(zip(
            [doc['_id'] for doc in docs],
            [self.process(doc['_source'], *args, **kwargs) for doc in docs]
            ))
        logger.debug("tested results: {updates}".format(**locals()))
        return updates
    
    def _parse_strings_that_contain_dicts(self, dict_in_a_string):
        '''parses dictionaries from string, for instance for commandline environments '''
        return ast.literal_eval(dict_in_a_string)
        
