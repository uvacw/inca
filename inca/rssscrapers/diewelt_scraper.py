import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
logger = logging.getLogger("INCA")

# Die Welt
class diewelt(rss):
    """Scrapes the latest news from welt.de"""

    def __init__(self):
        self.doctype = "die welt (www)"
        self.rss_url = "https://www.welt.de/feeds/latest.rss"
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
            category = tree.xpath('//*[@class="c-breadcrumb"]//a/span/text()')[1]
        except:
            category = ""
        # teaser
        try:
            teaser = " ".join(tree.xpath('//*[@class="c-summary__intro"]//text()'))
        except:
            teaser = ""
        teaser = teaser.strip()
        # title
        try:
            title1 = tree.xpath('//*[@class="rf-o-topic c-topic"]//text()')
        except:
            title1 = ""
        try:
            title2 = tree.xpath('//*[@class="c-headline o-dreifaltigkeit__headline rf-o-headline"]//text()')
        except:
            title2 = ""
        title = ": ".join(title1 + title2).strip().replace("\xa0", "")

        # text
        try:
            text = " ".join(tree.xpath('//*[@itemprop="articleBody"]//p/text()|//*[@itemprop="articleBody"]//h3/text()'))
        except:
            logger.warning("Text could not be accessed - most likely a premium article")
            text = ""
        ## firstletter
        try:
            firstletter = "".join(tree.xpath('//*[@itemprop="articleBody"]/p/span/text()'))
        except:
            firstletter = ""
        text = firstletter + text
        # author
        try:
            author = "".join(tree.xpath('//*[@class="c-author"]//a/text()'))
        except:
            logger.warning("No author")
            author = ""
        author = author.strip()

        extractedinfo = {
            "category": category,
            "title": title,
            "text": text,
            "teaser": teaser,
            "byline": author,
        }

        return extractedinfo