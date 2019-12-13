import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class handelsblatt(rss):
    """Scrapes handelsblatt.de"""

    def __init__(self):
        self.doctype = "handelsblatt (www)"
        self.rss_url = [
            "http://www.handelsblatt.com/contentexport/feed/schlagzeilen",
            "http://www.handelsblatt.com/contentexport/feed/wirtschaft",
            "http://www.handelsblatt.com/contentexport/feed/top-themen",
            "http://www.handelsblatt.com/contentexport/feed/finanzen",
            "http://www.handelsblatt.com/contentexport/feed/marktberichte",
            "http://www.handelsblatt.com/contentexport/feed/unternehmen",
            "http://www.handelsblatt.com/contentexport/feed/politik",
            "http://www.handelsblatt.com/contentexport/feed/technologie",
            "http://www.handelsblatt.com/contentexport/feed/panorama",
            "http://www.handelsblatt.com/contentexport/feed/sport",
            "http://www.handelsblatt.com/contentexport/feed/hbfussball",
        ]
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
                "".join(tree.xpath('//*[@class="vhb-article--introduction"]/text()'))
                .replace("\xa0", "")
                .replace("\n", "")
            )
        except:
            teaser = ""
        # title
        try:
            title = (
                " ".join(
                    tree.xpath(
                        '//*[@class="vhb-content"]/h2/span/text()|//*[@class="vhb-content"]/h2/span/span//text()'
                    )
                )
                .replace("\xa0", "")
                .replace("\n", "")
            )
        except:
            title = ""
        # text
        try:
            text = " ".join(
                tree.xpath(
                    '//*[@itemprop="articleBody"]/p/text()|//*[@itemprop="articleBody"]/p/em/text()|//*[@itemprop="articleBody"]/p/em/a/text()|//*[@itemprop="articleBody"]/p/a/text()|//*[@itemprop="articleBody"]/h3/strong/text()|//*[@itemprop="articleBody"]/h3/text()|//*[@itemprop="articleBody"]/h3/a/text()'
                )
            ).replace("\xa0", "")
        except:
            text = ""

        extractedinfo = {"title": title, "teaser": teaser, "text": text}

        return extractedinfo
