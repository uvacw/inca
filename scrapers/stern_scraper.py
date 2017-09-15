import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class stern(rss):
    """Scrapes stern.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "stern (www)"
        self.rss_url='http://www.stern.de/feed/standard/alle-nachrichten/'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=8, day=2)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        #category
        try:
            category = r[0]['url'].split('/')[3]
        except:
            category =""
        #somehow not clear with author and source and sometimes nothing
        #author
        #source
        try:
            source = tree.xpath('//*[@class="m-source"]//text()')[1]
        except:
            source =""
        #title (some articles have one and some two titles. this scraper takes both)
        try:
            title = tree.xpath('//*[@class="a-h1-title"]//text()')
        except:
            title =""
        #teaser
        try:
            teaser = tree.xpath('//*[@class="article-intro"]//text()')
        except:
            teaser =""
        #text
        try:
            text = tree.xpath('//*[@class="rtf-content-wrapper"]/p/text()')
        except:
            text =""
        extractedinfo = {"category":category,
                     "teaser":teaser,
                     "byline_source":source,
                     "title":title,
                     "text":text
                    }
        return extractedinfo