'''

This file contains the class for scrapers. Each scraper should 
inherit from this class and overwrite the 'get' function with 
a generator. 

Scrapers should yield dicts that contain the document (news article,
tweet, blogpost, whatever) 

'''
import logging
from core.document_class import Document
from celery.contrib.methods import task_method
from core.database import check_exists

logger = logging.getLogger(__name__)

class Scraper(Document):
    '''
    Scrapers are the generic way of adding new documents to the datastore. 
    
    Make scrapers in the 'scrapers' folder by using <datasource>_scraper.py as 
    the filename, containing a scraper which inherits from this class. 
    
    the 'get' method should be a self-powered retrieval task, with optional
    arguments.
    '''

    functiontype = 'scraper'
    language = ''
        
    def get(self):
        ''' This docstring should explain how documents are retrieved

        '''
        logger.warning("You forgot to overwrite the 'get' method of this scraper!")
        yield dict()

    def sideload(self, doc, doctype, language):
        '''
        This function side-loads documents, basically setting scraper doctype, language
        and metadata. 

        '''
        doc['doctype']  = self.doctype
        doc['language'] = self.language
        doc = self._add_metadata(doc)
        self._verify(doc)
        self._save_document(doc)
        
    def run(self, *args, **kwargs):
        '''
        DO NOT OVERWRITE THIS METHOD

        This is an internal function that calls the 'get' method and saves the 
        resulting documents. 
        '''
        logger.info("Started scraping")
        for doc in self.get(*args, **kwargs):
            doc['language'] = self.language
            doc = self._add_metadata(doc)
            self._verify(doc)
            self._save_document(doc)

    def _test_function(self):
        '''tests whether a scraper works by seeing if it returns at least one document
        
           GENERALLY DON'T OVERWRITE THIS METHOD!
        '''
        try:
            self.check_exists = lambda x: False # overwrite check exists to ensure start conditions
            for doc in self.get():
                logger.info("{self.__class__} works!".format(**locals()))
                return {"{self.__class__}".format(**locals()) :True}
        except:
            return {"{self.__class__}".format(**locals()) : False}
        
    def _check_exists(self, *args, **kwargs):
        return check_exists(*args, **kwargs)
