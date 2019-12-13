import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")

MAAND2INT = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


class shell(Scraper):
    """Scrapes Shell"""

    def __init__(self):
        self.START_URL = "http://www.shell.com/media/news-and-media-releases.html"
        self.BASE_URL = "http://www.shell.com/"
        self.doctype = "shell (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)

    def get(self, save):
        """                                                                             
        Fetches articles from Shell
        """

        releases = []

        overview_page = requests.get(self.START_URL)
        tree = fromstring(overview_page.text)

        linkobjects = tree.xpath("//h3//a")
        links = [self.BASE_URL + l.attrib["href"] for l in linkobjects]

        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            current_page = requests.get(link)
            tree = fromstring(current_page.text)
            try:
                title = " ".join(
                    tree.xpath('//*[@class="page-header__header"]/h1/text()')
                )
            except:
                print("no title")
                title = ""
            try:
                d = tree.xpath('//*/p[@class="page-header__date"]//text()')[0].strip()
                print(d)
                jaar = int(d[-4:])
                maand = MAAND2INT[d[:3].strip()]
                dag = int(d[4:-6])
                datum = datetime.datetime(jaar, maand, dag)
            except Exception as e:
                print("could not parse date")
                print(e)
                datum = None
            try:
                teaser = " ".join(
                    tree.xpath('//*[@class="page-header__text"]/p//text()')
                )
            except:
                teaser = ""
                teaser_clean = " ".join(teaser.split())
            try:
                text = " ".join(tree.xpath('//*[@class="text-image__text"]//text()'))
            except:
                logger.info("oops - geen textrest?")
                text = ""
            text = "".join(text)
            releases.append(
                {
                    "text": text.strip(),
                    "date": datum,
                    "teaser": teaser.strip(),
                    "title": title.strip(),
                    "url": link.strip(),
                }
            )

        return releases
