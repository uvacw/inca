'''
This file provides importing functionality
'''
from core.document_class import Document

class importer(Document):
    '''
    This object is used to import documents
    '''


    def run(self, input_iterable, doctype_field, input_description="unknown source", id_field=None, known_meta=[], force=False):
        '''imported from {input_description}'''.format(**locals())

        self.version = '.1'
        self.functiontype = 'importer'

        for document in input_iterable:
            self.doctype = document.get(doctype_field, doctype_field)
            document = self._add_metadata(document)
            self._verify(document)
            if id_field and id_field in document.keys():
                document['_id'] = document.get(id_field, None)
            self._save_document(document,forced=force)
