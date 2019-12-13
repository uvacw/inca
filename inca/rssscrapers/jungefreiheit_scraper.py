import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class jungefreiheit(rss):
    """Scrapes jungefreiheit.de"""

    def __init__(self):
        self.doctype = "junge freiheit (www)"
        self.rss_url = "https://jungefreiheit.de/feed/"
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
            category = tree.xpath('//*[@itemprop="name"]//span/text()')[0]
        except:
            category = ""
        # title1
        try:
            title1 = " ".join(
                tree.xpath('//*[@class="entry-header"]/div/a/text()')
            ).strip()
        except:
            title1 = ""
        # title2
        try:
            title2 = " ".join(tree.xpath('//*[@class="entry-title"]//text()')).strip()
        except:
            title2 = ""

        title = title1 + ": " + title2

        # author:
        try:
            author = tree.xpath('//*[@class="entry-author-name"]/a/text()')
        except:
            author = ""

        # teaser:no teaser on article page; rss_teaser as alternative.

        try:
            text = " ".join(
                tree.xpath(
                    '//*[@itemprop="text"]/p/text()|//*[@itemprop="text"]/p/a/text()|//*[@itemprop="text"]/p/strong/text()|//*[@itemprop="text"]/p/em/text()'
                )
            )
        except:
            text = ""

        extractedinfo = {
            "category": category,
            "byline": author,
            "text": text,
            "title": title,
        }

        return extractedinfo
