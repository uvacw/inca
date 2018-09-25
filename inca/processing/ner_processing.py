# -*- coding: utf-8 -*-
from ..core.processor_class import Processer
from ..core.basic_utils import dotkeys
import logging
import re
import sys

import spacy
import nl_core_news_sm

nlp = nl_core_news_sm.load()


logger = logging.getLogger("INCA")




class ner(Processer):
    '''Named Entity Recognition using spacy.io'''

    def process(self, document_field):
        '''NER based on spacy.io'''
        doc = nlp(document_field)
        nes = []
        for ent in doc.ents:
            nes.append({'text': ent.text, 
                       'start_char':ent.start_char, 
                       'end_char':ent.end_char, 
                       'label': ent.label_})
        return nes
