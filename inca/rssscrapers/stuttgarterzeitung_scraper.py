import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class stuttgarterzeitung(rss):
    """Scrapes the news from https://www.stuttgarter-zeitung.de/ """
    """Note for developers: The Stuttgarter Zeitung features a blog (https://www.stadtkind-stuttgart.de/). Currently, only the titles from this blog are parsed"""

    def __init__(self):
        self.doctype = "stuttgarter zeitung (www)"
        self.rss_url = [
            "https://www.stuttgarter-zeitung.de/news.rss.feed",
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

        # category
        try:
            category = tree.xpath(
                '//*[@class="brickgroup nav-breadcrumb cf"]//text()'
            )[8]
        except:
            category = ""
        category = category.replace("\n\t        \t\t", "")

        # title: consists out of two parts:
        # title1
        try:
            title1 = tree.xpath('//*[@class="mod-header-article"]/h1/em//text()|//*[@class="entry-title entry-title-single"]//text()')
        except:
            title1 = ""
        # title2
        try:
            title2 = tree.xpath('//*[@class="mod-header-article"]/h1/strong//text()')
        except:
            title2 = ""
        title = ": ".join(title1 + title2)
        # teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="box-lead"]//text()'))
        except:
            teaser = ""
        teaser = teaser.strip()
        # author
        try:
            author = tree.xpath('//*[@class="contentbrick box-author"]//text()|/*[@class="entry-author-name"]//text()')[0]
            if author.endswith("Von ") == True:
                author = tree.xpath('//*[@class="contentbrick box-author"]//text()')[1]
            else:
                author = author.replace("Von", "")
        except:
            author = ""
        author = author.strip().replace("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t", "").replace("\xa0", "")
        # text
        try:
            text = "".join(tree.xpath('//*[@class="brickgroup mod-article"]//p/text()'))
        except:
            logger.warning("Text could not be accessed - most likely a premium article")
            text = ""
        text = text.strip()
        
        extractedinfo = {
            "category": category,
            "title": title,
            "teaser": teaser,
            "text": text,
            "byline": author,
        }

        return extractedinfo