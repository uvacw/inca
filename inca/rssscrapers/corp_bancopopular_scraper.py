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


class popular(rss):
    """Scrapes Banco Popular"""

    def __init__(self):
        self.doctype = "banco popular (corp)"
        self.rss_url = "https://www.comunicacionbancopopular.es/feed/?post_type=nota"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=30)

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
                tree.xpath('//*/h3[@class="entry-title single-title"]//text()')
            ).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = "".join(
                tree.xpath('//*[@class="entry-content clearfix"]/strong/p//text()')
            ).strip()
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        teaser = " ".join(teaser.split())
        try:
            text = "".join(
                tree.xpath('//*[@class="entry-content clearfix"]/p//text()')
            ).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        releases = {
            "title": title.strip(),
            "teaser": teaser.strip(),
            "text": polish(text).strip(),
        }

        return releases
