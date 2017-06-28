# -*- coding: utf-8 -*-
from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging
import re
import sys
from nltk.sentiment import vader

# TODO: make sure that nltk.download('vader_lexicon') is called if lexicon is not available already.

logger = logging.getLogger(__name__)



class sentiment_vader_en(Processer):
    '''Sentiment-analyses English-language texts using Vader'''

    def process(self, document_field):
        '''Document was split into paragraphs'''
        senti=vader.SentimentIntensityAnalyzer()
        sentimentscores = senti.polarity_scores(document_field)
        return sentimentscores
