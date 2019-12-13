import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class sueddeutsche(rss):
    """Scrapes sueddeutsche.de"""

    def __init__(self):
        self.doctype = "sueddeutsche (www)"
        self.rss_url = (
            "http://rss.sueddeutsche.de/app/service/rss/alles/index.rss?output=rss"
        )
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
        # teaser:
        try:
            teaser = (
                " ".join(tree.xpath('//*[@class="body"]/ul/li/text()'))
                .replace("\n", "")
                .strip()
            )
        except:
            teaser = ""
        # title
        try:
            title = (
                "".join(
                    tree.xpath(
                        '//*[@class="header"]/h2/text()|//*[@class="header"]/h2/strong/text()'
                    )
                )
                .replace("\n        ", " ")
                .strip()
            )
        except:
            title = ""
        # text
        try:
            text = tree.xpath(
                '//*[@id="article-body"]/p/text()|//*[@id="article-body"]/p/a/text()'
            )
            if text[0].startswith("\n") == True:
                teaser = text[0].replace("\n", "").strip()
                text = " ".join(text[1:]).replace("\xa0", "")
            else:
                text = " ".join(text).replace("\xa0", "")
        except:
            text = ""
        # author
        try:
            author = "".join(
                tree.xpath(
                    '//*[@class="authorProfileContainer"]/span/strong/span/text()|//*[@class="authorProfileContainer"]/span/strong/text()'
                )
            ).strip()
            author = (
                author.replace("Von ", "")
                .replace("Kommentar von ", "")
                .replace("Interview von ", "")
            )
        except:
            author = ""
        # source
        try:
            source = "".join(
                tree.xpath('//*[@class="endofarticle__copyright"]//text()')[0].split(
                    "/"
                )[1:]
            )
        except:
            source = ""

        extractedinfo = {
            "title": title,
            "byline": author,
            "byline_source": source,
            "teaser": teaser,
            "text": text,
        }

        return extractedinfo
