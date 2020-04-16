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
        self.date = datetime.datetime(year=2020, month=4, day=8)

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
        try:
            category = tree.xpath('//*[@class="css-5m4t2m"]//a/text()')[0]
        except:
            category = ""
        # teaser
        try:
            teaser = " ".join(tree.xpath('//*[@class="css-1psf6fc"]/text()|//*[@class="css-13lgcsh"]//li/text()'))
        except:
            teaser = ""
        teaser = teaser.replace("\xa0", "")
        # title1
        try:
            title1 = tree.xpath('//*[@class="css-1keap3i"]/text()')
        except:
            title1 = ""
        # title2
        try:
            title2 = tree.xpath('//*[@class="css-1kuo4az"]/text()')
        except:
            title2 = ""
        title = ": ".join(title1 + title2)
        title = title.replace("\xa0", "")
        # text
        try:
            text = "".join(tree.xpath('//*[@class="sz-article__body css-uswvo e1lg1pmy0"]/p/text()|//*[@class="sz-article__body css-uswvo e1lg1pmy0"]/h3/text()|//*[@class="tickaroo-event-item-content-text"]//h2/text()|//*[@class="tickaroo-event-item-content-text"]//br/text()'))
        except:
            logger.warning("Text could not be accessed - most likely a premium article")
            text = ""
        text = text.replace("\xa0", "")
        # author
        try:
            author = tree.xpath('//*[@class="sz-article__byline css-141ob1d emhdic30"]//text()')
        except:
            logger.warning("No author")
            author = ""
        author = "".join(author).strip().replace(".css-viqvuv{border-bottom:1px solid #29293a;-webkit-text-decoration:none;text-decoration:none;-webkit-transition:border-bottom 150ms ease-in-out;transition:border-bottom 150ms ease-in-out;}.css-viqvuv:hover{border-bottom-color:transparent;}", "").replace("Von ", "").replace("Gastbeitrag von ", "").replace("Interview von ", "")
        
        extractedinfo = {
            "category": category,
            "title": title,
            "text": text,
            "teaser": teaser,
            "byline": author,
        }

        return extractedinfo