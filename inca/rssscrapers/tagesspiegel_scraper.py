import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class dertagesspiegel(rss):
    """Scrapes https://www.tagesspiegel.de"""

    def __init__(self):
        self.doctype = "der tagesspiegel (www)"
        self.rss_url = [
            "http://www.tagesspiegel.de/contentexport/feed/home",
            "http://www.tagesspiegel.de/contentexport/feed/politik",
            "http://www.tagesspiegel.de/contentexport/feed/queerspiegel",
            "http://www.tagesspiegel.de/contentexport/feed/wirtschaft",
            "http://www.tagesspiegel.de/contentexport/feed/sport",
            "http://www.tagesspiegel.de/contentexport/feed/kultur",
            "http://www.tagesspiegel.de/contentexport/feed/weltspiegel",
            "http://www.tagesspiegel.de/contentexport/feed/meinung",
            "http://www.tagesspiegel.de/contentexport/feed/medien",
            "http://www.tagesspiegel.de/contentexport/feed/wissen",
        ]
        self.version = ".1"
        self.date = datetime.datetime(year=2020, month=4, day=8)

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
            category = tree.xpath('//*[@class="ts-breadcrumb"]//*[@class="ts-inverse-link"]//text()')[0]
        except:
            category = ""

        # title: consists out of two parts:
        # title1
        try:
            title1 = tree.xpath('//*[@class="ts-overline"]//text()')[0]
        except:
            title1 = ""
        # title2
        try:
            title2 = tree.xpath('//*[@class="ts-headline"]//text()')[0]
        except:
            title2 = ""
        title = title1 + ": " + title2
        # teaser
        try:
            teaser = tree.xpath('//*[@class="ts-intro"]//text()')[0].replace("\n", "")
        except:
            teaser = ""
        # author
        try:
            author = tree.xpath('//*[@class="ts-author"]//a/text()')
        except:
            author = ""
        author = ", ".join(author).strip()
        # text
        try:
            text = "".join(tree.xpath('//*[@class="ts-article-content"]//p/text()'))
        except:
            logger.warning("Text could not be accessed - most likely a premium article")
            text = ""
        text = text.replace("\xa0", "")

        extractedinfo = {
            "category": category,
            "title": title,
            "teaser": teaser,
            "text": text,
            "byline": author,
        }

        return extractedinfo