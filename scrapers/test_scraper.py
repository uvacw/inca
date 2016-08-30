'''Test scraper that generates new documents for testing purposes
'''

import loremipsum
from core.scraper_class import Scraper
from random import randint

class testdocs(Scraper):
    '''Generates test documents'''
    doctype = "test_documents"
    version = "0.1"
    functiontype = "testcase_generator"

    def get(self, number=10, **kwargs):
        '''randomly generated document, title and text based on loremipsum module,
        image is a link to lorempixel random image'''
        start = randint(0,1000)
        for i in range(number):
            fake_id = i+start
            doc = {
                "_id" : "testdoc_{fake_id}".format(**locals()),
                "title" : prettier(loremipsum.get_sentence()),
                "text"  : prettier(loremipsum.get_paragraph()),
                "image" : "http://lorempixel.com/400/200/"
            }
            doc.update(kwargs)
            yield doc

def prettier(text):
    return text.replace("'","")