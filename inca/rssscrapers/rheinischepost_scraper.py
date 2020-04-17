import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
logger = logging.getLogger("INCA")


class rheinischepost(rss):
    """Scrapes the news from https://rp-online.de/ """

    def __init__(self):
        self.doctype = "rheinische post (www)"
        self.rss_url = [
            "https://rp-online.de/feed.rss",
            "https://rp-online.de/politik/feed.rss",
            "https://rp-online.de/wirtschaft/feed.rss",
            "https://rp-online.de/panorama/feed.rss",
            "https://rp-online.de/sport/feed.rss",
            "https://rp-online.de/kultur/feed.rss",
            "https://rp-online.de/panorama/feed.rss",
            "https://rp-online.de/panorama/wissen/feed.rss",
            "https://rp-online.de/leben/gesundheit/feed.rss",
            "https://rp-online.de/digitales/feed.rss",
            "https://rp-online.de/leben/auto/feed.rss",
            "https://rp-online.de/leben/reisen/feed.rss",
            "https://rp-online.de/leben/beruf/feed.rss", 
        ]
        self.version = ".1"
        self.date = datetime.datetime(year=2020, month=4, day=7)

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
            teaser = tree.xpath('//*[@class="park-article__intro park-article__content"]/text()')[1]
        except:
            teaser = ""
        teaser = "".join(teaser).strip().replace("\n", "")
        # author
        try:
            author = "".join(tree.xpath('//*[@class="park-article__sign"]/text()'))
        except:
            author = ""
        author = author.strip().replace("(", "").replace(")", "")
        # text
        try:
            text = "".join(tree.xpath('//*[@class="park-article-content"]//p/text()'))
        except:
            logger.warning("Text could not be accessed - most likely a premium article")
            text = ""
        # category
        try:
            category = tree.xpath('//*[@class="park-section-breadcrumb__link "]//span/text()')[1]
        except:
            category = ""

        extractedinfo = {
            "category": category,
            "title": title,
            "teaser": teaser,
            "text": text,
            "byline": author,
        }

        return extractedinfo