import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class focus(rss):
    """Scrapes focus.de"""

    def __init__(self):
        self.doctype = "focus (www)"
        self.rss_url = "http://rss.focus.de/fol/XML/rss_folnews.xml"
        self.version = ".1"
        self.date = datetime.datetime(year=2018, month=5, day=16)

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        """
        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("HTML tree cannot be parsed")
        # category
        try:
            category = tree.xpath('//*[@id="main"]//ol//a//text()')[1]
        except:
            category = ""

        # title
        try:
            title = " ".join(tree.xpath("//h1//text()"))

        except:
            title = ""

        # teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="leadIn"]//text()'))
        except:
            teaser = ""

        # text
        try:
            text = (
                " ".join(tree.xpath('//*[@class="textBlock"]//text()'))
                .replace("\xa0", "")
                .replace("\n", "")
                .replace("\t", "")
                .replace("\r", "")
            )
        except:
            text = ""
        # source
        try:
            source = tree.xpath('//*[@class="created"]//text()')
        except:
            source = ""

        extractedinfo = {
            "category": category,
            "teaser": teaser.strip(),
            "text": text.strip(),
            "bylinesource": source,
            "title": title,
        }

        return extractedinfo
