from lxml import html
from urllib import request
from lxml.html import fromstring
from inca.scrapers.rss_scraper import rss
from inca.core.scraper_class import Scraper
import re
import feedparser
import logging
import datetime
import locale
import requests
from lxml import etree

logger = logging.getLogger("INCA")


class taz(rss):
    """Scrapes http://www.taz.de"""

    def __init__(self):
        self.doctype = "die tageszeitung (www)"
        self.rss_url = "http://www.taz.de/!p4608;rss/"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=12, day=25)

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
            teaser = tree.xpath('//*[@class="intro "]/text()')[0]
        except:
            teaser = ""

        # text:
        try:
            text = (
                " ".join(
                    tree.xpath(
                        "//p[@class='article first odd']/text() | //p[@class='article odd']/text() | //p[@class='article even']/text() | //*[@class='sectbody']/h6//text() | //p[@class='article first odd']/a/text()| //p[@class='article odd']/a/text() | //p[@class='article even']/a/text() "
                    )
                )
                .replace("\xa0", "")
                .replace("|", "")
                .strip()
            )
        except:
            text = ""

        # title

        try:
            title = " ".join(
                tree.xpath(
                    '//*[@itemprop="articleBody"]/h4/text()|//*[@itemprop="articleBody"]/h1/text()'
                )
            ).replace("\n", "")
        except:
            title = ""
        # source
        try:
            source = "".join(tree.xpath('//*[@class="article first odd"]/em/text()'))
        except:
            source = ""

        extractedinfo = {
            "title": title,
            "text": text,
            "teaser": teaser,
            "byline_source": source,
        }

        return extractedinfo
