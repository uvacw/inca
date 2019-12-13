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


class telefonica(rss):
    """Scrapes Telefonica"""

    def __init__(self):
        self.doctype = "telefonica (corp)"
        self.rss_url = "https://www.telefonica.com/web/sala-de-prensa/rss/-/asset_publisher/RBb25zTLKrHp/rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=5)

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
            title = "".join(tree.xpath('//*/h1[@class="header-title"]//text()')).strip()
        except:
            logger.warning("Could not parse article title")
            title = ""
        try:
            teaser = "".join(
                tree.xpath('//*[@class="journal-content-article"]/ul//text()')
            ).strip()
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        teaser_clean = " ".join(teaser.split())
        try:
            text = "".join(
                tree.xpath(
                    '//*[@class="journal-content-article"]/p//text() | //*[@class="ca"]//text() | //*[@class="cg"]//text()'
                )
            ).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        releases = {
            "title": title.strip(),
            "teaser": teaser_clean.strip(),
            "text": polish(text).strip(),
        }

        return releases
