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


class diageopress(rss):
    """Scrapes diageo.com"""

    def __init__(self):
        self.doctype = "diageopress (corp)"
        self.rss_url = "https://www.diageo.com/en/rss/press-releases/"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)

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
        teaser    the intro to the artcile 
        text    the plain text of the article                                                                                                                                                                                                                              
        """

        tree = fromstring(htmlsource)
        try:
            title = "".join(
                tree.xpath(
                    '//*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-0"]/h1/text()'
                )
            ).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = "".join(tree.xpath('//*/p[@class="intro large"]//text()')).strip()
        except:
            teaser = ""
            teaser_clean = " ".join(teaser.split())
        try:
            text = "".join(tree.xpath('//*[@class="text-container"]/p//text()')).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        extractedinfo = {
            "title": title.strip(),
            "teaser": teaser.strip(),
            "text": polish(text).strip(),
        }

        return extractedinfo


class diageonews(rss):
    """Scrapes Diageo News"""

    def __init__(self):
        self.doctype = "diageonews (corp)"
        self.rss_url = "https://www.diageo.com/en/rss/all-news-and-media/"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)

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
                tree.xpath(
                    '//*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-2"]/h1/text() | //*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-2"]/h1/text() | //*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-0"]/h1/text()'
                )
            ).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            category = "".join(
                tree.xpath('//*//[@class="badge feature"]//text()')
            ).strip()
        except:
            category = ""
        if len(category.split(" ")) > 1:
            category = ""
        try:
            teaser = "".join(tree.xpath('//*/p[@class="intro large"]//text()')).strip()
        except:
            teaser = ""
            teaser_clean = " ".join(teaser.split())
        try:
            text = "".join(
                tree.xpath(
                    '//*[@class="text-container"]//text() | //*/p[@class="u-top-padding-half"]//text()'
                )
            ).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        extractedinfo = {
            "title": title.strip(),
            "category": category.strip(),
            "teaser": teaser.strip(),
            "text": polish(text).strip(),
        }

        return extractedinfo
