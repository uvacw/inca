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


class vopak(Scraper):
    """Scrapes Vopak"""

    def __init__(self):
        self.START_URL = "https://www.vopak.com/newsroom/press-and-news-releases"
        self.BASE_URL = "https://www.vopak.com/"
        self.doctype = "Vopak (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=11)

    def get(self, save):
        """                                                                             
        Fetches articles from Vopak
        """

        releases = []

        page = 0
        current_url = self.START_URL + "?field_date_filter_value=All&page=" + str(page)
        overview_page = requests.get(current_url)
        while overview_page.content.find(b"No results found") == -1:

            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*[@class="views-field views-field-title"]//a')
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
                    title = " ".join(tree.xpath('//*/h1[@class="title"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    d = tree.xpath('//*[@class="date-display-single"]//text()')[
                        0
                    ].strip()
                    print(d)
                    jaar = int(d[-4:])
                    maand = MAAND2INT[d[3:-4].strip()]
                    dag = int(d[:2])
                    datum = datetime.datetime(jaar, maand, dag)
                    print(datum)
                except Exception as e:
                    print("could not parse date")
                    print(e)
                    datum = None
                try:
                    text = " ".join(
                        tree.xpath('//*[@class="hugin"]//text() | //*/article//text()')
                    )
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append(
                    {
                        "text": text.strip(),
                        "date": datum,
                        "title": title.strip(),
                        "url": link.strip(),
                    }
                )

            page += 1
            current_url = (
                self.START_URL + "?field_date_filter_value=All&page=" + str(page)
            )
            overview_page = requests.get(current_url)

        return releases
