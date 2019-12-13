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


class bp(Scraper):
    """Scrapes BP"""

    def __init__(self):
        self.START_URL = (
            "http://www.bp.com/en/global/corporate/media/press-releases.html"
        )
        self.BASE_URL = "http://www.bp.com/"
        self.doctype = "BP (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

    def get(self, save):
        """                                                                             
        Fetches articles from BP
        """

        releases = []

        page = 1
        current_url = self.START_URL + "?page=" + str(page)
        overview_page = requests.get(current_url)
        while overview_page.content.find(b"Sorry, nothing found") == -1:

            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*/ul[@class="list"]/li//a')
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
                        tree.xpath('//*/h1[@class="nv-page-title"]/text()')
                    )
                except:
                    print("no title")
                    title = ""
                try:
                    teaser = " ".join(
                        tree.xpath('//*[@class="nv-richtext"]/h2//text()')
                    )
                except:
                    teaser = ""
                teaser_clean = " ".join(teaser.split())
                try:
                    d = tree.xpath('//*/strong[@class="nv-date"]//text()')[0].strip()
                    jaar = int(d[-4:])
                    dag = int(d[:2])
                    if len("dag") == 1:
                        maand = MAAND2INT[d[1:-5].strip()]
                    else:
                        maand = MAAND2INT[d[2:-5].strip()]
                    datum = datetime.datetime(jaar, maand, dag)
                except Exception as e:
                    print("could not parse date")
                    print(e)
                    datum = None
                try:
                    text = " ".join(
                        tree.xpath(
                            '//*[@class="nv-richtext"]/p//text() | //*[@class="nv-parsys-component nv-container"]//text()'
                        )
                    )
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append(
                    {
                        "text": text.strip(),
                        "teaser": teaser.strip(),
                        "date": datum,
                        "title": title.strip(),
                        "url": link.strip(),
                    }
                )

            page += 1
            current_url = self.START_URL + "?page=" + str(page)
            overview_page = requests.get(current_url)

        return releases
