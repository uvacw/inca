#import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from core.database import check_exists
import logging
import feedparser
import re

logger = logging.getLogger(__name__)



import urllib2
class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
    http_error_301 = http_error_303 = http_error_307 = http_error_302

cookieprocessor = urllib2.HTTPCookieProcessor()

opener = urllib2.build_opener(MyHTTPRedirectHandler, cookieprocessor)
urllib2.install_opener(opener)


class rss(Scraper):
    '''
    Reades a generic RSS feed and proceeds if items not already in collection.
    Retrieves full HTML content from link provided in RSS feed
    Yields docs with keys from RSS entry plus full HTML source of linked content.

    Subclasses should probably overwrite the following functions:
        By overwriting the parsehtml function, more keys can be extracted
        By overwriting the getlink function, modifications to the link can be made, e.g. to bypass cookie walls
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

            link=re.sub("/$","",self.getlink(post.link))

            if check_exists(_id)[0]==False:
                req=urllib2.Request(link, headers={'User-Agent' : "Wget/1.9"})
                htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")

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

    def getlink(self,link):
        '''
        Some sites require some modification of the URL, for example to pass a cookie wall.
        Overwrite this function with a function to do so if neccessary
        '''
        return link

if __name__=="__main__":
    rss().get()
