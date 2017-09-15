#import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from core.scraper_class import UnparsableException
from core.database import check_exists
import logging
import feedparser
import re

logger = logging.getLogger(__name__)



try: # assumes python 2
    import urllib2
    from urllib2 import HTTPRedirectHandler
    from urllib2 import HTTPCookieProcessor

except: # in case of python 3.X
    import urllib.request as urllib2
    from urllib.request import HTTPRedirectHandler
    from urllib.request import HTTPCookieProcessor

class MyHTTPRedirectHandler(HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
    http_error_301 = http_error_303 = http_error_307 = http_error_302

cookieprocessor = HTTPCookieProcessor()

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

    def __init__(self,database=True):
        Scraper.__init__(self,database)
        self.doctype = "rss"
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

    def get(self,**kwargs):
        '''Document collected via {} feed reader'''.format(self.doctype)

        # This RSS-scraper is a generic fallback option in case we do not have
        # any specific one. Therefore, only use the following generic values
        # if we do not have any more specific info already
        if 'rss_url' in kwargs:
            RSS_URL=kwargs['rss_url']
        else:
            try: RSS_URL=self.rss_url
            except: RSS_URL='N/A'

        assert RSS_URL != 'N/A','You need to specify the feed URL. Example: rss_url="http://www.nu.nl/rss"'
        
        if type(RSS_URL) is str:
            RSS_URL=[RSS_URL]

        for thisurl in RSS_URL:
            rss_body = self.get_page_body(thisurl)
            d = feedparser.parse(rss_body)
            for post in d.entries:
                try:
                    _id=post.id
                except:
                    _id=post.link

                link=re.sub("/$","",self.getlink(post.link))

                if self.database==False or check_exists(_id)[0]==False:
                    try:
                        req=urllib2.Request(link, headers={'User-Agent' : "Wget/1.9"})
                        htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                    except:
                        htmlsource=None
                        logger.info('Could not open link - will not retrieve full article')
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
                           "title_rss":post.title,
                           "teaser_rss":teaser,
                           "publication_date":datum,
                           "htmlsource":htmlsource,
                           "feedurl":thisurl,
                           "url":re.sub("/$","",post.link)}
                    if htmlsource is not None:
                        # TODO: CHECK IF PARSEHTML returns None, if so, raise custom exception
                        parsed = self.parsehtml(doc['htmlsource'])
                        if parsed is None or parsed =={}:
                            try:
                                raise UnparsableException
                            except UnparsableException:
                                pass
                        else:
                            doc.update(parsed)
                    parsedurl = self.parseurl(link)
                    doc.update(parsedurl)
                    docnoemptykeys={k: v for k, v in doc.items() if v}
                    yield docnoemptykeys

    def get_page_body(self,url,**kwargs):
        '''Makes an HTTP request to the given URL and returns a string containing the response body'''
        request = urllib2.Request(url, headers={'User-Agent' : "Wget/1.9"})
        response_body = urllib2.urlopen(request).read().decode(encoding="utf-8",errors="ignore")
        return response_body

    def parsehtml(self,htmlsource):
        '''
        Parses the html source and extracts more keys that can be added to the doc
        Empty in this generic fallback scraper, should be replaced by more specific scrapers
        '''
        return dict()

    def parseurl(self,url):
        '''
        Parses the url source and extracts more keys that can be added to the doc
        Empty in this generic fallback scraper, can be replaced by more specific scrapers
        if the URL itself needs to be parsed. Typial use case: The url contains the 
        category of the item, which can be parsed from it using regular expressions
        or .split('/') or similar.
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
