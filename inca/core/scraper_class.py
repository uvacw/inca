'''

This file contains the class for scrapers. Each scraper should
inherit from this class and overwrite the 'get' function with
a generator.

Scrapers should yield dicts that contain the document (news article,
tweet, blogpost, whatever)

For the following keys, please provide the information specified below:

doctype             : The medium or outlet (e.g. volkskrant, guardian, economist)
url                 : URL from which data is scraped (e.g. volkskrant.nl/artikel1)
publication_date    : Date of publication of article/website as specified by outlet, NOT SCRAPING
text                : Plain (no code/XML or HTML tags) text content

OPTIONAL, BUT RECOMMENDED

_id       : a unique, preferably same as external source identifier of the document (e.g. ISBN, DOI )
language  : If you can safely assume the language of specified documents, please specify them here

'''
import logging
from core.document_class import Document
from core.database import check_exists, DATABASE_AVAILABLE

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
    #language = ''

    def __init__(self,database=True):
        Document.__init__(self,database)

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
        #doc['language'] = self.language)
        doc = self._add_metadata(doc)
        self._verify(doc)
        self._save_document(doc)

    def run(self, save=True, startpage = 1, maxpages = 2, maxreviewpages = 5, maxurls = 50, maxfora = 2, maxthreads=2, forumid = None, pagename = "groenlinks", app_id = "appID", app_secret = "appSecret", starturl = "starturl", *args, **kwargs):
        
        '''
        DO NOT OVERWRITE THIS METHOD

        This is an internal function that calls the 'get' method and saves the
        resulting documents.
        '''
        self.STARTPAGE = startpage
        self.MAXPAGES = maxpages
        self.MAXREVIEWPAGES = maxreviewpages
        self.MAXURLS = maxurls
        self.MAXFORA = maxfora
        self.MAXTHREADS = maxthreads
        self.FORUMID = forumid
        self.PAGENAME = pagename
        self.APP_ID = app_id
        self.APP_SECRET = app_secret
        self.STARTURL = starturl

        logger.info("Started scraping")
        if save == True:
            for doc in self.get(*args, **kwargs):
                if type(doc)==dict:
                    doc = self._add_metadata(doc)
                    self._save_document(doc)
                else:
                    doc = self._add_metadata(doc)
                    self._save_documents(doc)
        else:
            return [self._add_metadata(doc) for doc in self.get(*args, **kwargs)]

        logger.info('Done scraping')

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

class UnparsableException(Exception):
    def __init__(self):
        logger.warn('Could not parse the content; maybe the string does not contain valid HTML?')
