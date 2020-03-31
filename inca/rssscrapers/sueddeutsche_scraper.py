import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
logger = logging.getLogger("INCA")

# Die Welt - Politik
class diesueddeutsche(rss):
    """Scrapes the latest news from sueddeutsche.de"""

    def __init__(self):
        self.doctype = "sueddeutschet politik (www)"
        self.rss_url = "https://rss.sueddeutsche.de/app/service/rss/alles/index.rss?output=rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2020, month=3, day=29)

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        category       sth. like economy, sports, ...
        teaser         the teaser of an article
        bulletpoints   the bbulletpoints at the start of an article (either the only content, or serving as a teaser)
        text           the plain text of the article
        byline         the author, e.g. "Bob Smith"
        
        """
        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("HTML tree cannot be parsed")

        # category
        """ The following code's output it a list with the general category first, followed by more detailled category descriptions"""
        try:
            category = tree.xpath('//*[@class="css-5m4t2m"]//a/text()')
        except:
            category = ""

        # teaser
        try:
            teaser = " ".join(
                tree.xpath('//*[@class="css-1psf6fc"]/text()')
            )
        except:
            teaser = ""
        # bulletpoints
        try:
            bulletpoints = " ".join(
                tree.xpath('//*[@class="css-13lgcsh"]//li/text()')
            )
        except:
            bulletpoints = ""
        # title1
        try:
            title1 = tree.xpath(
                '//*[@class="css-1keap3i"]/text()'
            )
        except:
            title1 = ""
        # title2
        try:
            title2 = tree.xpath(
                '//*[@class="css-1kuo4az"]/text()'
            )
        except:
            title2 = ""
        title = ": ".join(title1 + title2)

        # text
        try:
            text = "".join(tree.xpath('//*[@class="sz-article__body css-uswvo e1lg1pmy0"]/p/text()|//*[@class="sz-article__body css-uswvo e1lg1pmy0"]/h3/text()'))
        except:
            text = ""
         
        # author
        try:
            author = tree.xpath('//*[@class="sz-article__byline css-141ob1d emhdic30"]//text()')
        except:
            author = ""

        extractedinfo = {
            "category": category,
            "title": title,
            "text": text,
            "teaser": teaser,
            "byline": author,
            "bulletpoints": bulletpoints,
        }

        return extractedinfo