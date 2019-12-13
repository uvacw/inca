import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class stern(rss):
    """Scrapes stern.de"""

    def __init__(self):
        self.doctype = "stern (www)"
        self.rss_url = "https://www.stern.de/feed/standard/alle-nachrichten/"
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
        # category: First all articles are in the category 'newsticker' and only later they re put into the proper categories. Therefore no category variable for this scraper.

        # somehow not clear with author and source and sometimes nothing
        # author
        # source
        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("HTML tree cannot be parsed")

        try:
            source = tree.xpath('//*[@class="m-source"]//text()')[1]
        except:
            source = ""
        # title (some articles have one and some two titles. this scraper takes both)
        try:
            title = (
                "".join(tree.xpath('//*[@class="article"]//div//h2//text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            title = ""
        # teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="article-intro"]//text()'))
        except:
            teaser = ""
        # text
        try:
            text = (
                " ".join(
                    tree.xpath(
                        '//*[@class="article"]//*[@itemprop="articleBody"]/p//text()'
                    )
                )
                .replace("\n           ", "")
                .replace("\xa0", "")
                .strip()
            )
        except:
            text = ""

        extractedinfo = {
            "teaser": teaser,
            "byline_source": source,
            "title": title,
            "text": text,
        }
        return extractedinfo
