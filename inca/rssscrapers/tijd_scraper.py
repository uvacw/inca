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


class detijd(rss):
    """Scrapes tijd.nl"""

    def __init__(self):
        self.doctype = "detijd (www)"
        self.rss_url = [
            "http://www.tijd.be/rss/ondernemen.xml",
            "http://www.tijd.be/rss/politiek.xml",
            "http://www.tijd.be/rss/markten_live.xml",
            "http://www.tijd.be/rss/opinie.xml",
            "http://www.tijd.be/rss/cultuur.xml",
            "http://www.tijd.be/rss/netto.xml",
            "http://www.tijd.be/rss/sabato.xml",
        ]
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=8, day=2)

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
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                             
        category    sth. like economy, sports, ...                                                                                                                                                                                                                          
        """

        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen", type(doc), len(doc))
            print(doc)
            return ("", "", "", "")
        try:
            author = tree.xpath('//*[@class="m-meta__item-container"]//a/text()')[0]
        except:
            author = ""
            logger.debug("Could not parse article source")
        try:
            textfirstpara = tree.xpath(
                '//*[@class="l-main-container-article__intro highlightable "]/text()'
            ).strip()
        except:
            textfirstpara = ""
            logger.debug("Could not parse article teaser")
        try:
            textrest = "".join(
                tree.xpath(
                    '//*[@class="l-main-container-article__body clearfix highlightable "]//text()'
                )
            ).strip()
        except:
            textrest = ""
            logger.warning("Could not parse article text")
        try:
            category = tree.xpath(
                '//*[@class="m-breadcrumb__item--last"]/a/span/text()'
            )[0]
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            title = "".join(
                tree.xpath(
                    '//*[@class="l-grid__item desk-big-five-sixths push-desk-big-one-sixth"]//text()'
                )
            ).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")

        texttotal = textfirstpara + " " + textrest
        extractedinfo = {
            "title": title,
            "text": texttotal.strip(),
            "byline": author.strip(),
            "category": category.strip(),
        }

        return extractedinfo
