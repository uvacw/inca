# -*- coding: utf-8 -*-
from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging
import re
from pattern.nl import parse
# TODO I now use pattern.nl as it was basically copy/paste from the earlier version
# TODO we might want to port this to Alpino, if we use Alpino anyway
from sys import maxunicode
import unicodedata

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
            
class njr(Processer):
    '''Keeps only nouns (N), adjectives (J), and adverbs (R) (N, J, R are Penn Treebank tags)'''

    def process(self, document_field):
        '''everything except nouns, adjectives, and adverbs was removed'''
        doc = ""
        for sentence in parse(document_field).split():
                for token in sentence:
                    if token[1].startswith('N') or token[1].startswith('J') or token[1].startswith('R'):
                        doc+=(" "+token[0])
        return doc

class remove_punctuation(Processer):
    '''removes all punctuation. "Bla. Bla bla+" -> "Bla Bla bla". "Willem-Alexander" -> WillemAlexander'''
    try:  #assume python2
        tbl = dict.fromkeys(i for i in xrange(maxunicode) if unicodedata.category(unichr(i)).startswith('P'))
    except:   #but do this in python3
        tbl = dict.fromkeys(i for i in range(maxunicode) if unicodedata.category(chr(i)).startswith('P'))

    def process(self, document_field):
        '''punctuation removed'''
         return document_field.replace(u"`",u"").replace(u"´",u"").translate(remove_punctuation.tbl)

class lowercase(Processer):
    '''converts to lowercase'''
    def process(self, document_field):
        '''converted to lowercase'''
        return document_field.lower()