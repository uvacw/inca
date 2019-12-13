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
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


class aegon(Scraper):
    """Scrapes aegon"""

    def __init__(self):
        self.START_URL = "https://www.aegon.com/en/Home/Investors/News-releases/"
        self.BASE_URL = "https://www.aegon.com/"
        self.doctype = "aegon (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)

    def get(self, save):
        """                                                                             
        Fetches articles from Aegon
        """

        releases = []
        tree = fromstring(requests.get(self.START_URL).text)

        linkobjects = tree.xpath(
            '//*[@class="overviewpage-section"][1]/div/div/h4[@class="item-header"]//a'
        )
        links = [self.BASE_URL + l.attrib["href"] for l in linkobjects]

        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            tree = fromstring(requests.get(link).text)
            try:
                title = "".join(
                    tree.xpath(
                        '//*[@class="header-container"]/h1//text() | //*[@class="header-container lang-switch-single"]/h1//text()'
                    )
                ).strip()
            except:
                print("no title")
                title = ""
            try:
                d = tree.xpath('//*[@class="date"]//text()')[0].strip()
                print(d)
                jaar = int(d[-4:])
                maand = MAAND2INT[d[2:-4].strip()]
                dag = int(d[:2])
                datum = datetime.datetime(jaar, maand, dag)
            except Exception as e:
                print("could not parse date")
                print(e)
                datum = None
            try:
                teaser = "".join(
                    tree.xpath('//*[@class="aeg-intro"]/p//text()')
                ).strip()
            except:
                print("no teaser")
                teaser = ""
                teaser_clean = " ".join(teaser.split())
            try:
                text = "".join(
                    tree.xpath('//*[@class="aeg-xhtml-content"]//text()')
                ).strip()
            except:
                print("geen text")
                logger.info("oops - geen textrest?")
                text = ""
            text = "".join(text)
            releases.append(
                {"title": title.strip(), "teaser": teaser.strip(), "text": text.strip()}
            )

        return releases
