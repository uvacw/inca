import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
import requests

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


class thesun(rss):
    """Scrapes thesun.co.uk"""

    def __init__(self):
        self.doctype = "thesun (www)"
        self.rss_url = "https://www.thesun.co.uk/feed/"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=8)

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                

        Parameters                                                                                                                                                                                                                                                      
        ----                                                                                                                                                                                                                                                               
        htmlsource: string                                                                                                                                                                                                                                                  
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                  
        teaser    the intro to the artcile                                                                                                                                                                                                                                  
        byline      the author, e.g. "Bob Smith"                                                                                                                                                                                                                            
        text    the plain text of the article                                                                                                                                                                                                                               
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = " ".join(
                tree.xpath("//*[@class='article__headline-section']//text()")
            )
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = " ".join(
                tree.xpath("//*[@class='article__subdeck theme__border-color']//text()")
            )
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            byline = " ".join(tree.xpath("//*[@class='article__author']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            text = " ".join(tree.xpath("//*[@class='article__content']/p//text()"))
        except:
            text = ""
            logger.warning("Could not parse article source")

        extractedinfo = {
            "title": title.strip(),
            "teaser": teaser.strip(),
            "byline": byline.strip().replace("\t", "").replace("\n", ""),
            "text": text.strip()
            .replace("\xa0", "")
            .replace("\\", "")
            .replace("\t", "")
            .replace("\n", ""),
        }

        return extractedinfo

    def parseurl(self, url):
        """
        Parses the category based on the url
        """
        category = url.split("/")[3]
        return {"category": category}
