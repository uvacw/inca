import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class jungleworld(rss):
    """Scrapes jungle.world.de"""

    def __init__(self):
        self.doctype = "jungleworld (www)"
        self.rss_url = ["https://jungle.world/rss.xml"]

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
            category = tree.xpath('//*[@class="breadcrumb"]//li/a/text()')[-1]
        except:
            category = ""
        # title

        try:
            title1 = (
                "".join(
                    tree.xpath('//*[@class="field field-name-field-dachzeile"]//text()')
                )
                .replace("\n", "")
                .replace("\t", "")
                .strip()
            )
        except:
            title1 = ""
        try:
            title2 = (
                tree.xpath('//*[@class="page-title"]//text()')[0]
                .replace("\n", "")
                .replace("\t", "")
                .strip()
            )
        except:
            title2 = ""
        title = title1 + ": " + title2
        # teaser
        try:
            teaser = (
                "".join(tree.xpath('//*[@class="lead"]//text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            teaser = ""

        # text
        try:
            text = " ".join(tree.xpath('//*[@class="ft"]/p/text()')).replace("\xad", "")
        except:
            text = ""

        # author
        try:
            author = tree.xpath('//*[@class="autor"]/a/text()')[0]
        except:
            author = ""

        extractedinfo = {
            "category": category,
            "teaser": teaser.strip(),
            "byline": author,
            "title": title.strip(),
            "text": text,
        }

        return extractedinfo
