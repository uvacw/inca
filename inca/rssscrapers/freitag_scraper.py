import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class freitag(rss):
    """Scrapes freitag.de"""

    def __init__(self):
        self.doctype = "der freitag (www)"
        self.rss_url = "https://www.freitag.de/@@RSS"
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

        # teaser
        try:
            teaser = (
                " ".join(tree.xpath('//*[@class="abstract column"]/text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            teaser = ""
        # title
        try:
            title = "".join(
                tree.xpath('//*[@class="title column"]/text()').replace("\n", "")
            ).strip()
        except:
            title = ""
        # text
        try:
            text = " ".join(
                tree.xpath(
                    '//*[@class="column s-article-text x-article-text js-dynamic-advertorial js-external-links"]/p/text()|//*[@class="column s-article-text x-article-text js-dynamic advertorial js-external-links"]/p/em/text()|//*[@class="column s-article-text x-article-text js-dynamic advertorial js-external-links"]/h2/text()'
                )
            ).replace("\n", "")
        except:
            text = ""
        # category
        try:
            category = (
                " ".join(tree.xpath('//*[@class="abstract column"]/strong/text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            category = ""
        # author
        try:
            author = (
                "".join(tree.xpath('//*[@class="author"]/a/text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            author = ""

        extractedinfo = {
            "title": title,
            "text": text,
            "byline": author,
            "teaser": teaser,
            "category": category,
        }

        return extractedinfo
