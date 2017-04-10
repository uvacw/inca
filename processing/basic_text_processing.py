# -*- coding: utf-8 -*-
from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging
import re
import sys

try:
    from pattern.nl import parse
except:
    '''sorry, python 2 only'''
    pass

# TODO I now use pattern.nl as it was basically copy/paste from the earlier version
# TODO we might want to port this to Alpino, if we use Alpino anyway
from sys import maxunicode
import unicodedata

logger = logging.getLogger(__name__)

if sys.version_info.major == 2:
    from pattern.nl import parse
else:
    logger.warn("Pattern is NOT python 3 compatible...skipping")
    def parse(*args, **kwargs):
        raise "Unavailable in python3!"

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


class replace(Processer):
    '''Replaces text based on regular expressions.
    Three positional arguments by default: document_field, regexp, replace_with
    Searches for regexp and replaces it with replace_with
    Optionally, specify:
    regexp_2nd = REGEXP - if a condition is fulfilled, replace
                 regexp_2nd with replace_with as well.
    By default, the condition is that the _first_ regexp has to be matched at least
    N = 1 times. This can be changed by specifying cond:
    cond = INT | REGEXP - if an integer, then the first regexp has to be matched INT times
                 if a REGEXP, then this regular expression has to be matched (but not replaced)

    Examples:
    process('text', regexp='ABN.?Amro', replace_with='ABN_Amro')
       replaces 'ABN.?Amro' with 'ABN_Amro'
    process('text',regexp='ABN.?Amro', replace_with='ABN_Amro', regexp_2nd='\bABN\b')
       additonally replaces '\bABN\b' with 'ABN_Amro' if 'ABN.?Amro' has been found at least once
    process('text',regexp='ABN.?Amro', replace_with='ABN_Amro', regexp_2nd='\bABN\b', cond=2)
       additionally replaces '\bABN\b' with 'ABN_Amro' if 'ABN.?Amro' has been found at least twice
    process('text',regexp='ABN.?Amro', replace_with='ABN_Amro', regexp_2nd='\bABN\b', cond='[Bb]ank')
       additionally replaces '\bABN\b' with 'ABN_Amro' if '[Bb]ank' has been found at least once

    Possible use cases: If Jan Bakker is mentioned, assume all following Bakker's to be Jan Bakker.
    If VVD is mentioned, assume Rutte to be Mark Rutte.
    '''
    def process(self, document_field, **kwargs):
        '''text replaced based on regular expression rules'''
    #,replace_with, regexp_2nd=None,cond=1

        r = re.subn(str(kwargs['regexp']), kwargs['replace_with'], document_field)
        doc = r[0]
        if 'cond' in kwargs:
            cond = kwargs['cond']
        else:
            cond = 1
        if 'regexp_2nd' in kwargs and isinstance(cond,int) and r[1]>=cond:
            # if regexp_2nd is specified, then replace this regular expression as well
            # but only if the first one was matched at least COND times.
            # example use case: regexp='ABN.?Amro', replace_with='ABN_Amro',regexp_2nd '\bABN\b'
            # if 'ABN.?Amro' is found and replaced at least once, then also replace
            # '\bABN\b' with 'ABN_Amro'
            # Or: replace Bert.?Bakker with Bert_Bakker, and all subsequent
            # Bakker's also with Bert_Bakker (as they will be most likely be
            # about Bert_Bakker as well and not Piet_Bakker
            doc=re.sub(str(kwargs['regexp_2nd']), kwargs['replace_with'], doc)
        elif 'regexp_2nd' in kwargs and isinstance(cond,str):
            # alternatively, the condition can be specified as a regular expression that has to be
            # matched at least once without any replacement
            # example use case: replace Rutte with Mark_Rutte if VVD is mentioned in the same article
            if re.findall(str(cond),doc):
                doc=re.sub(str(kwargs['regexp_2nd']), kwargs['replace_with'], doc)
        return doc


class multireplace(Processer):
    '''Like replace, but expexts the keyword 'rules' with a list of dicts as input. Example:
    rules = [{'regexp':'...', 'replace_with':'...'}, {'regexp':'...', 'replace_with':'...','regexp_2nd='...',cond='...'}]
    regexp and replace_with are mandatory keys, regexp_2nd and cond are optional'''
    def process(self, document_field, **kwargs):
        '''text replaced based on regular expression rules'''
        doc = document_field
        for rule in kwargs['rules']:
            r = re.subn(str(rule['regexp']), rule['replace_with'], doc)
            doc = r[0]
            if 'cond' in rule:
                cond = rule['cond']
            else:
                cond = 1
            if 'regexp_2nd' in rule and isinstance(cond,int) and r[1]>=cond:
                doc=re.sub(str(rule['regexp_2nd']), rule['replace_with'], doc)
            elif 'regexp_2nd' in rule and isinstance(cond,str):
                if re.findall(str(cond),doc):
                    doc=re.sub(str(rule['regexp_2nd']), rule['replace_with'], doc)
        return doc

