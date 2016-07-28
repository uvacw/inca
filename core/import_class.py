'''
This file provides importing functionality
'''
from core.document_class import Document
import datetime
import logging
logger = logging.getLogger(__name__)

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
                document['_id'] = str(document.get(id_field, None))
            try:
                self._save_document(document,forced=force)
            except Exception as e:
                print("ACK: {e}".format(**locals()))