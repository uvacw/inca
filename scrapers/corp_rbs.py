# DOESN'T WORK PROPERLY

import requests
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

class rbs(rss):
    """Royal Bank of Scotland"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "RBS (corp)"
        self.rss_url ='https://www.rbs.com/rbs/rss/news.rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=30)

    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h2[@class="header-group__sign-post tile--signpost-text"]//text()')).strip()
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*/p[@class="stand-first-text"]//text()')).strip()
        except:
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="comp-rich-text "]/p//text()')).strip()
        except:
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        releases={"title":title.strip(),
                  "teaser":teaser.strip(),
                  "text":polish(text).strip()
                  }

        return releases