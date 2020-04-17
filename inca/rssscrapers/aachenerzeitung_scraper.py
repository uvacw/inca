import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class aachenerzeitung(rss):
    """Scrapes the news from https://www.aachener-zeitung.de. Note"""

    def __init__(self):
        self.doctype = "aachener zeitung (www)"
        self.rss_url = [
            "https://www.aachener-zeitung.de/politik/feed.rss",
            "https://www.aachener-zeitung.de/wirtschaft/feed.rss",
            "https://www.aachener-zeitung.de/kultur/feed.rss",
            "https://www.aachener-zeitung.de/ratgeber/feed.rss",
            "https://www.aachener-zeitung.de/panorama/feed.rss",
            "https://www.aachener-zeitung.de/sport/feed.rss",
            "https://www.aachener-zeitung.de/nrw-region/feed.rss",
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
            category = tree.xpath('//*[@class="park-section-breadcrumb__link "]//span/text()')[1]
        except:
            category = ""
        # title: consists out of two parts, a kicker and a headline:
        # title1
        try:
            title1 = tree.xpath('//*[@class="park-article__kicker"]/text()')
        except:
            title1 = ""
        # title2
        try:
            title2 = tree.xpath('//*[@class="park-article__headline"]/text()')
        except:
            title2 = ""
        title = title1 + title2
        title = ": ".join(title).strip().replace("\n", "").replace("         ", "").replace("        ", "")
        if title.startswith(":") == True:
            title = title.strip().replace(":", "")
        else:
            title = title
        # teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="park-article__intro park-article__content"]/text()')).strip().replace("\n", "")
        except:
            teaser = ""
        # author
        try:
            author = "".join(tree.xpath('//*[@class="park-article__sign"]/text()'))
        except:
            author = ""
        author = author.replace("(", "").replace(")", "")
        # text
        try:
            text = "".join(tree.xpath('//*[@class="park-article-content"]//p/text()'))
        except:
            logger.warning("Text could not be accessed - most likely a premium article")
            text = ""

        extractedinfo = {
            "category": category,
            "teaser": teaser,
            "title": title,
            "text": text,
            "byline": author,
        }

        return extractedinfo