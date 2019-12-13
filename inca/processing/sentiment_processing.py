# -*- coding: utf-8 -*-
from ..core.processor_class import Processer
from ..core.basic_utils import dotkeys
import logging
import re
import sys
from nltk.sentiment import vader


logger = logging.getLogger("INCA")

try:
    from pattern.nl import parse
except ImportError:
    logger.warn("Pattern seems to be missing, please reinstall.")
    def parse(*args, **kwargs):
        raise "Unavailable because you don't have the pattern library installed"

    pass


class sentiment_vader_en(Processer):
    """Sentiment-analyses English-language texts using Vader"""

    def process(self, document_field):
        """Added sentiment based on Vader"""
        try:
            senti = vader.SentimentIntensityAnalyzer()
            sentimentscores = senti.polarity_scores(document_field)
            return sentimentscores
        except LookupError:
            from nltk import download

            download("vader_lexicon")
            logger.error(
                "Couldn't find Vader Lexicon, downloaded it\nYou will have to re-run the processor"
            )


class sentiment_pattern(Processer):
    """Sentiment-analyses using Pattern"""

    def process(self, document_field, *args, **kwargs):
        """Added sentiment based on Pattern"""
        try:
            language = kwargs["language"]
        except:
            raise Exception(
                "Specify a language, for example language='nl'. We support nl, en, fr, and it"
            )

        if language == "nl":
            try:
                from pattern.nl import sentiment
            except:
                raise Exception(
                    "Unavailable because you don't have the pattern library installed"
                )
        elif language == "en":
            try:
                from pattern.en import sentiment
            except:
                raise Exception(
                    "Unavailable because you don't have the pattern library installed"
                )
        elif language == "fr":
            try:
                from pattern.fr import sentiment
            except:
                raise Exception(
                    "Unavailable because you don't have the pattern library installed"
                )
        elif language == "it":
            try:
                from pattern.it import sentiment
            except:
                raise Exception(
                    "Unavailable because you don't have the pattern library installed"
                )
        else:
            raise Exception(
                "Specify a language, for example language='nl'. We support nl, en, fr, and it"
            )

        sent = sentiment(document_field)
        return {"polarity": sent[0], "subjectivity": sent[1]}
