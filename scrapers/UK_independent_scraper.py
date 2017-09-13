import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging
import requests

logger = logging.getLogger(__name__)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class independent(rss):
    """Scrapes independent.co.uk"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "independent (www)"
        self.rss_url = "http://www.independent.co.uk/rss"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=12)

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
            logger.warning("cannot parse?",type(doc),len(doc))
            logger.warning(doc)
            return("","","", "")
        try:
            title = " ".join(tree.xpath("//*[@itemprop='headline']/text()"))
        except:
            title = ""
            logger.info("No 'title' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            teaser = " ".join(tree.xpath("//*[@class='intro']/p/text()"))
        except:
            teaser = ""
            logger.info("No 'teaser' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            byline = " ".join(tree.xpath("//*[@itemprop='name']//text()"))
        except:
            byline = ""
            logger.info("No 'byline' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            category = " ".join(tree.xpath("//*[@property='item']//text()"))
        except:
            category = ""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")    
        try:
            text = " ".join(tree.xpath("//*[@class='text-wrapper']/p/text()"))
        except:
            text = ""
            logger.info("No 'text' field encountered - don't worry, maybe it just doesn't exist.")
            
    
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip().replace("\xa0",""),
                       "byline":byline.strip(),
                       "category":category.strip(),
                       "text":text.strip()
                      }

        return extractedinfo 