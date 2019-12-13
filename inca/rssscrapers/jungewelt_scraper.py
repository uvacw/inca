import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class jungewelt(rss):
    """Scrapes jungewelt.de"""

    def __init__(self):
        self.doctype = "junge welt (www)"
        self.rss_url = "https://www.jungewelt.de/feeds/newsticker.rss"
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
            title = "".join(tree.xpath('//*[@class="Article"]//h1/text()'))
        except:
            title = ""

        # category: this newssite has strange categeories:
        try:
            category = tree.xpath('//*[@class="Date"]//text()')[3].split("/", 1)[1]
        except:
            category = ""
        # author
        try:
            author = (
                tree.xpath('//*[@class="Article"]//address/text()')[0]
                .replace("Von", "")
                .strip()
            )

        except:
            author = ""
        # teaser
        try:
            teaser = (
                tree.xpath('//*[@class="Article"]//h2/text()')[0]
                .replace("Von", "")
                .strip()
            )
        except:
            teaser = ""
        # text
        try:
            text = (
                "".join(
                    tree.xpath(
                        '//*[@class="Content"]/p/text()|//*[@class="Content"]/p/em/text()'
                    )
                )
                .strip()
                .replace("\n", "")
            )
        except:
            text = ""
            print(htmlsource)

        # check if paywall
        paywall = tree.xpath('//*[@id ="ID_LoginFormFailed"]')
        if paywall:
            paywall_na = True
        else:
            paywall_na = False

        extractedinfo = {
            "title": title,
            "byline": author,
            "text": text,
            "teaser": teaser,
            "category": category,
            "paywall_na": paywall_na,
        }

        return extractedinfo
