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


class vodafone(Scraper):
    """Scrapes Vodafone"""

    def __init__(self):
        self.START_URL = (
            "http://www.vodafone.com/content/index/media/vodafone-group-releases.html"
        )
        self.BASE_URL = "http://www.vodafone.com/"

    def get(self, save):
        """                                                                             
        Fetches articles from Vodafone
        """
        self.doctype = "Vodafone (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

        releases = []

        page = 0
        current_url = self.START_URL + "?category=all&offset=" + str(page) + "0"
        overview_page = requests.get(current_url)
        while overview_page.text.find("search-results-list") != -1:

            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*[@class="col lrg-50"]/h3//a')
            links = [
                self.BASE_URL + l.attrib["href"]
                for l in linkobjects
                if "href" in l.attrib
            ]

            for link in links:
                logger.debug("ik ga nu {} ophalen".format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title = " ".join(
                        tree.xpath(
                            '//*[@class="belt  "]/h1/text() | //*[@class="belt no-img "]/h1/text()'
                        )
                    )
                except:
                    print("no title")
                    title = ""
                try:
                    teaser = " ".join(
                        tree.xpath(
                            '//*[@class="article-blockquote"]/blockquote/p//text()'
                        )
                    )
                except:
                    teaser = ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    d = tree.xpath('//*[@class="subs-date"]//text()')[0].strip()
                    jaar = int(d[-4:])
                    maand = MAAND2INT[d[2:-4].strip()]
                    dag = int(d[:2])
                    datum = datetime.datetime(jaar, maand, dag)
                except Exception as e:
                    print("could not parse date")
                    print(e)
                    datum = None
                try:
                    text = " ".join(
                        tree.xpath('//*[@class="richtexteditor section"]/p//text()')
                    )
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append(
                    {
                        "text": text.strip(),
                        "title": title.strip(),
                        "date": datum,
                        "teaser": teaser.strip(),
                        "url": link.strip(),
                    }
                )

            page += 1
            current_url = self.START_URL + "?category=all&offset=" + str(page) + "0"
            overview_page = requests.get(current_url)

        return releases
