import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from core.database import check_exists
import logging
import feedparser
import re

logger = logging.getLogger(__name__)



class rss(Scraper):
    '''
    Reades a generic RSS feed and proceeds if items not already in collection.
    Retrieves full HTML content from link provided in RSS feed
    Yields docs with keys from RSS entry plus full HTML source of linked content
    By overwriting the parsehtml function, more keys can be extracted
    '''
    
    def get(self,**kwargs):
        '''Document collected via {} rss feed reader'''.format(self.doctype)

        # This RSS-scraper is a generic fallback option in case we do not have
        # any specific one. Therefore, only use the following generic values
        # if we do not have any more specific info already
        if 'rss_url' in kwargs:
            RSS_URL=kwargs['rss_url']
        else:
            RSS_URL=self.rss_url
        if not self.doctype:
            self.doctype = "rss"
        if not self.version:
            self.version = ".1"
        if not self.date:
            self.date    = datetime.datetime(year=2016, month=8, day=2)

        assert RSS_URL,'You need to specify the feed URL. Example: rss_url="http://www.nu.nl/rss"'

        d = feedparser.parse(RSS_URL)

        for post in d.entries:
            try:
                _id=post.id
            except:
                _id=post.link

            if check_exists(_id)[0]==False:
                req=requests.get(re.sub("/$","",post.link), headers={'User-Agent' : "Wget/1.9"})
                htmlsource=req.text
                try:
                    teaser=re.sub(r"\n|\r\|\t"," ",post.description)
                except:
                    teaser=""
                try:
                    datum=datetime.datetime(*feedparser._parse_date(post.published)[:6])
                except:
                    try:
                        # alternative date format as used by nos.nl
                        datum=datetime.datetime(*feedparser._parse_date(post.published[5:16])[:6])
                    except:
                        #print("Couldn't parse publishing date")
                        datum=None
                doc = {"_id":_id,
                       "title":post.title,
                       "teaser":teaser,
                       "publication_date":datum,
                       "htmlsource":htmlsource,
                       "feedurl":RSS_URL,
                       "url":re.sub("/$","",post.link)}
                doc.update(self.parsehtml(doc['htmlsource']))
                docnoemptykeys={k: v for k, v in doc.items() if v}
                yield docnoemptykeys

    def parsehtml(self,htmlsource):
        '''
        Parses the html source and extracts more keys that can be added to the doc
        Empty in this generic fallback scraper, should be replaced by more specific scrapers
        '''
        return dict()
            
if __name__=="__main__":
    rss().get()
