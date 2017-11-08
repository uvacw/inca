'''
This file contains functionality to repair errors in the database,
for instance to re-parse the raw html source and/or to re-download
the HTML source
'''

from core.processor_class import Processer
from core.database import update_document, get_document, check_exists
from dateutil import parser
import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class reparse(Processer):
    '''
    Sometimes, content is not correctly parsed, because a scraped site
    might have changed their layout. This allows to re-parse content
    by specifiying the new function to parse the content
    '''

    def process(self, document,  source_field, parsefunction):
        '''reparses {source_field}'''.format(**locals())
        pass

    def run(self, document, source_field, parsefunction, save=False):
        '''
        Takes a document and a parsing function and re-parses the HTML source.

        Parameters
        ---
        document: dict or string
            INCA-document that needs to be reparsed.
            Either a dict with the full document or a string with the document id
        source_field: string
            key of the field that contains the HTML source
        parsefunction
            a Python function to parse the HTML source
        save
            whether the result should be returned or stored to the database

        Example
        ---
        p = inca.processing.repair_processing.reparse()
        p.run('https://www.nu.nl/-/4959386/','htmlsource',inca.scrapers.news_scraper.nu.parsehtml)
    
        '''

        if not (type(document) == dict and '_source' in document.keys()):

            if check_exists(document):
                document = get_document(document)
            else:
                logger.debug("document retrieval failure {document}".format(**locals()))
                return document

        newfields = parsefunction(self, document['_source'][source_field])
        document['_source'].update(newfields)
            
        if save:
            update_document(document, force=True)

        else:
            return document

class redownload(Processer):
    '''
    Sometimes, content is not correctly downloaded, for instance due to
    a new cookie wall. This allows to re-download the content
    by specifiying the new function to download the content
    '''

    def process(self, document,  url_field, parsefunction):
        '''re-downloads {url_field}'''.format(**locals())
        pass

    def run(self, document, url_field, html_field, downloadfunction, save=False):
        '''
        Takes a document and a parsing function and re-parses the HTML source.

        Parameters
        ---
        document: dict or string
            INCA-document that needs to be reparsed.
            Either a dict with the full document or a string with the document id
        url_field: string
            key of the field that contains the URL
        html_field: string
            key of the field in which to store the downloaded content 
        downloadfunction
            a Python function to download the URL
        save
            whether the result should be returned or stored to the database

        Example
        ---
        p = inca.processing.repair_processing.reparse()
        p.run('https://www.nu.nl/-/4959386/','url','htmlsource',inca.scrapers.news_scraper.nu.get_page_body)
    
        '''

        if not (type(document) == dict and '_source' in document.keys()):

            if check_exists(document):
                document = get_document(document)
            else:
                logger.debug("document retrieval failure {document}".format(**locals()))
                return document

        document['_source'][html_field] = downloadfunction(self, document['_source'][url_field])  
        if save:
            update_document(document, force=True)

        else:
            return document
