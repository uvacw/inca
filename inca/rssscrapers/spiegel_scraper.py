import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")

# Der Spiegel
class spiegel(rss):
    """Scrapes http://www.spiegel.de"""

    def __init__(self):
        self.doctype = "spiegel (www)"
        self.rss_url = ["http://www.spiegel.de/schlagzeilen/index.rss"]

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
            category = tree.xpath(
                '//*[@id="wrapper"]//*[@class="current-channel-name"]//text()'
            )[0]
        except:
            category = ""
        # title
        try:
            title1 = tree.xpath('//*[@class="headline-intro"]//text()')[0]
        except:
            title1 = ""

        try:
            title2 = tree.xpath('//*[@class="headline"]//text()')[0]
        except:
            title2 = ""

        title = title1 + ": " + title2
        # teaser
        try:
            teaser = tree.xpath('//*[@class="article-intro"]//text()')[0]
        except:
            teaser = ""

        # text
        try:
            text = (
                " ".join(
                    tree.xpath(
                        '//*[@class="article-section clearfix"]//p//text()|//*[@class="article-section clearfix"]/blockquote/i/text()'
                    )
                )
                .replace("\n", "")
                .replace("\x85", "")
            )
        except:
            text = ""

        # author
        try:
            author = tree.xpath('//*[@class="author"]/a/text()')[0]
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
