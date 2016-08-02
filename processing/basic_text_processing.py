from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging
import re

logger = logging.getLogger(__name__)

class clean_whitespace(Processer):
    '''Changes multiple whitespace to single whitespace'''

    def process(self, document_field):
        '''multiple whitespaces were folded to single whitespaces'''
        return re.sub(r'(\n\n|[ \t\n]|\r\n)([ \t\n\r\n])+', r'\1', document_field)

class split_texts(Processer):
    '''Splits text into a list of paragraphs'''

    def process(self, document_field, split_values=['\r\n','\n\n']):
        '''Document was split into paragraphs'''

        doc = [document_field]
        for splitter in split_values:
            splittable = [doc.pop(num) for num,part in enumerate(doc) if splitter in part]
            [doc.extend(splittable.split(splitter)) for splittable in doc]
        return doc
            
