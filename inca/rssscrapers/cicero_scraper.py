import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class cicero(rss):
    """Scrapes cicero.de"""

    def __init__(self):
        self.doctype = "cicero (www)"
        self.rss_url = ["http://cicero.de/rss.xml"]

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
            category = r[0]["url"].split("/")[3]
        except:
            category = ""
        # title
        try:
            title1 = (
                tree.xpath('//*[@itemprop="headline"]//span/text()')[0]
                .strip()
                .replace("\n", "")
            )
        except:
            title1 = ""

        try:
            title2 = (
                tree.xpath('//*[@class="h1 font-41-sans-serif"]//text()')[0]
                .strip()
                .replace("\n", "")
            )
        except:
            title2 = ""

        title = title1 + ": " + title2
        # teaser
        try:
            teaser = tree.xpath('//*[@class="lead"]//text()')[0]
        except:
            teaser = ""

        # text
        try:
            text = (
                " ".join(
                    tree.xpath(
                        '//*[@class="field field-name-field-cc-body"]/p//text()|//*[@class="field field-name-field-cc-body"]/h3//text()'
                    )
                )
                .replace("\xa0", "")
                .replace("\n", "")
            )
        except:
            text = ""

        # author
        try:
            author = tree.xpath('//*[@class="teaser-small__metadata"]//a/text()')
        except:
            author = ""

        extractedinfo = {
            "category": category,
            "teaser": teaser.strip(),
            "byline": author,
            "title": title.strip(),
            "text": text.strip(),
        }

        return extractedinfo
