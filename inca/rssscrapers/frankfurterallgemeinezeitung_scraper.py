import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class faz(rss):
    """Scrapes faz.net"""

    def __init__(self):
        self.doctype = "faz (www)"
        self.rss_url = "http://www.faz.net/rss/aktuell/"
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
            category = tree.xpath('//*[@class="gh-LogoStage_Top"]//span/text()')[0]
        except:
            category = ""
        # teaser
        try:
            teaser = (
                "".join(tree.xpath('//*[@id="TOP"]//*[@class="atc-IntroText"]//text()'))
                .replace("\n", "")
                .replace("\t", "")
            )

        except:
            teaser = ""
        # title
        try:
            title = (
                "".join(
                    tree.xpath(
                        '//*[@class="atc-Header"]/div/h2/span/text()|//*[@class="atc-Header"]/div/h2/span/span/text()|//*[@class="atc-Header atc-Header-comment"]/div/div/h2/span/span/text()|//*[@class="atc-Header atc-Header-comment"]/div/div/h2/span/text() '
                    )
                )
                .replace("\n", "")
                .replace("\t", "")
            )
        except:
            title = ""

        # text: still has mistakes in it. scrapes more than just the text. also includes adds between the text.

        # First letter:
        try:
            firstletter = " ".join(tree.xpath('//*[@class="atc-Text "]/p/span/text()'))

        except:
            firstletter = ""
        # Text:
        try:
            text = " ".join(
                tree.xpath(
                    '//*[@class="atc-Text "]/p/text()|//*[@class="atc-Text "]/p/a/text()'
                )
            )

        except:
            text = ""
        text = firstletter + text
        # author
        try:
            author = (
                "".join(tree.xpath('//*[@class="atc"]//header//a//text()'))
                .replace("\t", "")
                .replace("\n", "")
                .strip()
            )
        except:
            author = ""
        # source
        try:
            source = (
                "".join(tree.xpath('//*[@class="quelle"]//text()'))
                .replace("Quelle:", "")
                .replace("\r", "")
                .replace("\n", "")
            )
        except:
            source = ""

        extractedinfo = {
            "category": category,
            "title": title,
            "byline": author,
            "byline_source": source,
            "teaser": teaser,
            "text": text,
        }

        return extractedinfo
