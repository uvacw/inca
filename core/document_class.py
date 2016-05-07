'''
This document class is the template for classes that add or update
documents in the database. The scraper and update classes inherit
from this class. 

The basic functionality is adding meta-data 

'''

import logging
import datetime
import inspect

logger = logging.getLogger(__name__)

from core.database import document_collection

class Document(object):
    '''
    Scrapers are the generic way of adding new documents to the datastore. 
    
    '''

    functiontype = ''
    version      = ''
    date         = ''
    
    def __init__(self):
        self._check_complete()
        pass

    def _save_document(self, document, forced=False):
        '''
        Documents are saved to the general document collection
        defined in the core.database file. 

        Note that by default, documents can only extend, not replace
        old documents. 

        '''
        if document.get('_id',False) and not forced:
            old_document = document_collection.find_one({'_id':document.get('_id')})
            document.update(old_document)
        document_collection.insert(document)

    def _add_metadata(self,document, **kwargs):
        '''
        DO NOT OVERWRITE THIS FUNCTION

        This method generates the metadata for returned documents based on 
        the 'get' function docstring and arguments.

        All new keys are reflected in the 'META' key with the information 
        about the script in question. 

        '''
        meta = dict(
            ADDED_AT              = datetime.datetime.now(),
            ADDED_METHOD          = self.get.__doc__,
            FUNCTION_VERSION      = self.version,
            FUNCTION_VERSION_DATE = self.date,
            FUNCTION_TYPE         = self.functiontype,
            FUNCTION_ARGUMENTS    = kwargs
            )

        if not document.get('META',False):
            document['META']=dict()

        for key in document.keys():
            if key == 'META': continue
            if key not in document['META'].keys():
                document['META'][key] = meta
        
    def _verify(self, document):
        '''
        DO NOT OVERWRITE THIS FUNCTION

        This method verifies whether yielded documents conform to the specification 
        of the datastore
        '''
        assert document.has_key('meta')
        assert type(document)==dict
        for key in document.keys():
            if key=='META': continue
            assert key in document['META']

    def _check_complete(self):
        '''
        DO NOT OVERWRITE THIS FUNCTION

        This method checks whether the appropriate information is present in the subclass. 
        '''

        for attribute in ['functiontype','version','date']:
            if not getattr(self,attribute):
                logger.warning("%s misses the appropriate `%s` property! Please set these in the class __init__ method as self.%s" %(self.__class__, attribute,attribute))

        teststrings = [''' This docstring should explain how documents are transformed ''', ''' This docstring should explain how documents are retrieved ''' ]

        for method in ['process','get']:
            try:
                if getattr(self,method).__doc__ in teststrings:
                    logger.warning("%s's %s docstring does not reflect functionality! please update the docstring in your class definition." %(self.__class__, method))
            except:
                pass
