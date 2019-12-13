import requests
import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


def polish(textstring):
    # This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split("\n")
    lead = lines[0].strip()
    rest = "||".join([l.strip() for l in lines[1:] if l.strip()])
    if rest:
        result = lead + " ||| " + rest
    else:
        result = lead
    return result.strip()


class boskalispress(rss):
    """Scrapes Boskalis Westminster Press Releases"""

    def __init__(self):
        self.doctype = "boskalispress (corp)"
        self.rss_url = "https://boskalis.com/syndication/press-releases/feed.rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                
        
        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                             
        htmlsource: string                                                                                                                                                                                                                                                
            html retrived from RSS feed                                                                                                                                                                                                                                     
        
        yields                                                                                                                                                                                                                                                            
        ----                                                                                                                                                                                                                                                             
        title    the title of the article                                                                                                                                                                                                                                 
        category    sth. like economy, sports, ...
        text    the plain text of the article                                                                                                                                                                                                                              
        """

        tree = fromstring(htmlsource)
        try:
            title = "".join(
                tree.xpath('//*/h1[@class="heading--section"]/text()')
            ).strip()
        except:
            logger.warning("Could not parse article title")
            title = ""
        try:
            category = "".join(
                tree.xpath('//*/a[@class="btn btn--link"]//text()')
            ).strip()
        except:
            logger.debug("Could not parse article category")
            category = ""
        if len(category.split(" ")) > 1:
            category = ""
        try:
            text = "".join(
                tree.xpath('//*[@class="page-content content--main"]//text()')
            ).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        extractedinfo = {
            "title": title.strip(),
            "category": category.strip(),
            "text": polish(text).strip(),
        }

        return extractedinfo


class boskalisnews(rss):
    """Scrapes Boskalis Westminster News Releases"""

    def __init__(self):
        self.doctype = "boskalisnews (corp)"
        self.rss_url = "https://boskalis.com/syndication/news-releases/feed.rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)

    def parsehtml(self, htmlsource):
        """                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        """
        tree = fromstring(htmlsource)
        try:
            title = "".join(
                tree.xpath('//*/h1[@class="heading--section"]/text()')
            ).strip()
        except:
            logger.warning("Could not parse article title")
            title = ""
        try:
            category = "".join(tree.xpath('//*/span[@class="tag"]//text()')).strip()
        except:
            category = ""
        if len(category.split(" ")) > 1:
            category = ""
        try:
            text = "".join(
                tree.xpath('//*[@class="page-content content--main"]//text()')
            ).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        extractedinfo = {
            "title": title.strip(),
            "category": category.strip(),
            "text": polish(text).strip(),
        }

        return extractedinfo
