import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

class diewelt(rss):
    """Scrapes welt.de"""

    def __init__(self):
        self.doctype = "diewelt (www)"
        self.rss_url='https://www.welt.de/feeds/topnews.rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2018, month=5, day=16)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("HTML tree cannot be parsed")

#category
        try:
            category = tree.xpath('//*[@class="c-breadcrumb"]//a/span/text()')[1]
        except:
            category =""

#teaser
        try:
            teaser = ' '.join(tree.xpath('//*[@class="c-summary__intro"]//text()'))
        except:
            teaser =""
#title1
        try:
            title1 = tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()')[1]
        except:
            title1 =""
#title2
        try:
            title2 = tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()')[3]
        except:
            title2 = ""
            
        title = title1 + ": " +  title2
#text
        try:
            text = ' '.join(tree.xpath('//*[@itemprop="articleBody"]/p/text()|//*[@itemprop="articleBody"]/h3/text()'))
        except:
            text =""
#firstletter
        try:
            firstletter = ' '.join(tree.xpath('//*[@itemprop="articleBody"]/p/span/text()'))
        except:
            firstletter  =""
#author
        try:
            author1 = tree.xpath('//*[@class="c-author__name"]//a/text()')
            if len(author1)==2:
                author = tree.xpath('//*[@class="c-author__name"]//a/text()')[0]
            else:
                author=""
        except:
            author=""
                                                                             
#source
        try:
            source = tree.xpath('//*[@class="c-source"]//text()')
        except:
            source =""
            
        extractedinfo={"category":category,
                       "title":title,
                       "text":firstletter + text,
                       "teaser":teaser,
                       "byline":author,
                       "byline_source":source
                       }
        
        return extractedinfo
