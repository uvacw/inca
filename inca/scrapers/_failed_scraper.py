import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class _failed(rss):
    """Retrieves RSS feed from hbvl.be, but returns None as parsed content. FOR TESTING AND DEBUGGING ONLY"""

    def __init__(self):
        self.doctype = "belangvanlimburg (www)"
        self.rss_url = (
            "http://www.hbvl.be/rss/section/0DB351D4-B23C-47E4-AEEB-09CF7DD521F9"
        )

        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        """

        return None
