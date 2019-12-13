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


class independent_uk(rss):
    """Scrapes independent.co.uk"""

    def __init__(self):
        self.doctype = "independent-uk (www)"
        self.rss_url = "http://www.independent.co.uk/rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=12)

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
        category    sth. like economy, sports, ... 
        text    the plain text of the article                                                                                                                                      
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Cannot parse HTML tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = " ".join(tree.xpath("//*[@itemprop='headline']/text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = " ".join(tree.xpath("//*[@class='intro']/p/text()"))
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            byline = " ".join(tree.xpath("//*[@itemprop='name']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article byline")
        try:
            category = " ".join(tree.xpath("//*[@property='item']//text()"))
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            text = " ".join(
                tree.xpath(
                    "//*[@class='text-wrapper']/p/text()|//*[@class='body-content']/p/descendant-or-self::text()"
                )
            )
        except:
            text = ""
            logger.warning("Could not parse article teaser")

        extractedinfo = {
            "title": title.strip(),
            "teaser": teaser.strip().replace("\xa0", ""),
            "byline": byline.strip(),
            "category": category.strip(),
            "text": text.strip(),
        }

        return extractedinfo
