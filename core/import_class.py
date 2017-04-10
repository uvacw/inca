'''
This file provides importing functionality
'''
from core.document_class import Document
import datetime
import logging
logger = logging.getLogger(__name__)
from core.database import config
try:
    import pymongo
except:
    logger.warning('No MongoDB support')

class importer(Document):
    '''
    This object is used to import documents
    '''


    def run(self, input_iterable, doctype_field, input_description="unknown source", id_field=None, force=False):
        '''imported from external source'''

        self.version = '.1'
        self.functiontype = 'importer'
        self.date = datetime.datetime(year=2016, month=7, day=27)

        for num,document in enumerate(input_iterable):
            logger.info('processing {num}'.format(**locals()))
            self.doctype = document.get(doctype_field, doctype_field)
            document = self._add_metadata(document)
            self._verify(document)
            if id_field and id_field in document.keys():
                document['_id'] = str(document.get(id_field, None))  #DO WE REALY WANT THIS? "None" as string?
            try:
                self._save_document(document,forced=force)
            except Exception as e:
                logger.warning("ACK, unable to import document number {num}: {e}".format(**locals()))


class mongoimporter(importer):
    '''
    This is an importer to import old-style INCA databases in MongoDB format
    '''

    def run(self, query = {}, force=False, authenticate=False):
        '''imported from MongoDB'''

        self.version = '.1'
        self.functiontype = 'importer'
        self.date = datetime.datetime(year=2017, month=4, day=4)

        databasename=config.get('mongodb','databasename')
        collectionname=config.get('mongodb','collectionname')
        username=config.get('mongodb','username')
        password=config.get('mongodb','password')
        client = pymongo.MongoClient(config.get('mongodb','url'))
        db = client[databasename]
        if authenticate:
            db.authenticate(username,password)
        collection = db[collectionname]

        mapping = {'doctype':'source',
                   'url':'url',
                   '_id':'rssidentifier',
                   'publication_date':'datum',
                   'text':'text',
                   'teaser':'teaser',
                   'title':'title',
                   'byline':'byline',
                   'bylinesource':'bylinesource',
                   'category':'section',
                   'url':'url'}
        
        input_iterable = collection.find(query)

        
        for num,inputdoc in enumerate(input_iterable):
            document={}
            for k,v in mapping.items():
                try:
                    document[k] = inputdoc[v]
                except:
                    logger.debug('key {} not found'.format(k))
            logger.info('processing {num}'.format(**locals()))
            self.doctype = document.get('doctype')
            document = self._add_metadata(document)
            self._verify(document)
            # logger.debug('about to save',document)
            print('\n'*10)
            try:
                self._save_document(document,forced=force)
                logger.debug("Stored document {} in ES".format(num))
            except Exception as e:
                logger.warning("ACK, unable to import document number {num}: {e}".format(**locals()))

