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


class dailystar(rss):
    """Scrapes dailystar.co.uk"""

    def __init__(self):
        self.doctype = "dailystar (www)"
        self.rss_url = "http://feeds.feedburner.com/daily-star-Latest-News"
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
            logger.warning("Cannot parse HTML tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = tree.xpath("//*[@itemprop='headline']//text()")[0]
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = tree.xpath("//*[@id='singleArticle']/header/p/text()")[0]
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            byline = tree.xpath("//*[@class='author']//text()")[0]
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            text = " ".join(tree.xpath("//*[@data-type='article-body']//p/text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")

        extractedinfo = {
            "title": title.strip(),
            "teaser": teaser.strip(),
            "byline": byline.strip(),
            "text": text.replace("\r\n", "").replace("\\", "").strip(),
        }

        return extractedinfo
