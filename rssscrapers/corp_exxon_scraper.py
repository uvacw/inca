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

class exxonmobil(rss):
    """Scrapes ExxonMobil"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "exxonmobil (corp)"
        self.rss_url ='http://exxonmobil.newshq.businesswire.com/feeds/press_release/all/rss.xml'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=5, day=3)


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
            title="".join(tree.xpath('//*[@class="title"]/text()')).strip()
            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            teaser="".join(tree.xpath('//*[@class="bwlistitemmargb"]/text()')).strip()
            print("this prints teaser dirty", teaser)
        except:
            print("no teaser")
            teaser= ""
        teaser_clean = " ".join(teaser.split())
        try:
            text_dirty = "".join(tree.xpath('//*[@class="bw-main-content"]//p/text()')).strip()
            print(type(text_dirty))
            print(text_dirty)
        except:
            logger.info("oops - geen text?")
            text_dirty = ""
        text = polish(text_dirty)
        releases={"title":title.strip(),
                  "teaser":teaser_clean.strip(),
                  "text":text.replace("\n"," ").strip()
                  }

        return releases