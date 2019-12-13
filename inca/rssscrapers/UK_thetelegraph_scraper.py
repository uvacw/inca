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


class thetelegraph(rss):
    """Scrapes telegraph.co.uk"""

    def __init__(self):
        self.doctype = "thetelegraph (www)"
        self.rss_url = "http://www.telegraph.co.uk/rss.xml"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=11)

    def parsehtml(self, htmlsource):
        """        
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                             
        
        Parameters                                                                                                                                                                                                                                                          
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 

        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        category    sth. like economy, sports, ...                                                                                                                                                                                                                         
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
            title = "".join(tree.xpath("//*[@class='headline__heading']/text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath("//*[@class='breadcrumbs__item-content']/text()")[1]
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            byline = "".join(tree.xpath("//*[@class='byline__author-name']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            text = "".join(
                tree.xpath(
                    "//*[@itemprop='articleBody']//p/text()|//*[@itemprop='articleBody']//a/text()|//*[@class='m_first-letter m_first-letter--flagged']//text()"
                )
            )
        except:
            byline = ""
            logger.debug("Could not parse article source")

        extractedinfo = {
            "title": title.strip().replace("\n", ""),
            "category": category.strip(),
            "byline": byline.strip().replace("\n", "").replace(",", ""),
            "text": text.strip().replace("\xa0", "").replace("\\", ""),
        }

        return extractedinfo
