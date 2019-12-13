import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class zeit(rss):
    """Scrapes zeit.de"""

    def __init__(self):
        self.doctype = "zeit (www)"
        self.rss_url = "http://newsfeed.zeit.de/all"
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
        # title
        try:
            title = "".join(tree.xpath('//*[@class="article-header"]//h1/span/text()'))
        except:
            title = ""
        # category
        try:
            category = tree.xpath(
                '//*[@id="navigation"]//*[@class="nav__ressorts-link--current"]//text()'
            )
        except:
            category = ""
        # author
        try:
            author = tree.xpath('//*[@itemprop="author"]/a/span/text()')
        except:
            author = ""
        # source
        try:
            source = (
                tree.xpath('//*[@class="metadata"]//span/text()')[0]
                .replace("Quelle:", "")
                .strip()
            )

        except:
            source = ""
        # teaser
        try:
            teaser = (
                "".join(tree.xpath('//*[@class="summary"]//text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            teaser = ""
        # text
        try:
            text = (
                "".join(tree.xpath('//*[@class="paragraph article__item"]//text()'))
                .strip()
                .replace("\n", "")
            )

        except:
            text = ""

        extractedinfo = {
            "title": title,
            "category": category,
            "teaser": teaser,
            "byline": author,
            "byline_source": source,
            "text": text,
        }

        return extractedinfo
