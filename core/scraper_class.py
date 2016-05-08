'''

This file contains the class for scrapers. Each scraper should 
inherit from this class and overwrite the 'get' function with 
a generator. 

Scrapers should yield dicts that contain the document (news article,
tweet, blogpost, whatever) 

'''
import logging
from core.document_class import Document

logger = logging.getLogger(__name__)

class Scraper(Document):
    '''
    Scrapers are the generic way of adding new documents to the datastore. 
    
    Make scrapers in the 'scrapers' folder by using <datasource>_scraper.py as 
    the filename, containing a scraper which inherits from this class. 
    
    '''

    functiontype = 'scraper'
        
    def get(self):
        ''' This docstring should explain how documents are retrieved '''
        logger.warning("You forgot to overwrite the 'get' method of this scraper!")
        yield dict()

    def _get_document(self):
        '''
        This is an internal function that calls the 'get' method and saves the 
        resulting documents. 
        '''
        for doc in self.get():
            doc['doctype'] = self.doctype
            doc = self._add_metadata(doc)
            self._verify(doc)
            self._save_document(doc)
            
        
