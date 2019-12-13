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


class abf(Scraper):
    """Scrapes Associated British Foods"""

    def __init__(self):
        self.START_URL = "https://www.abf.co.uk/media/news"
        self.BASE_URL = "http://www.abf.co.uk/"
        self.doctype = "ABF (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=29)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            try:
                tree = fromstring(requests.get(link).text)
                try:
                    title = " ".join(tree.xpath('//*[@class="content-main"]/h1/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    # eerste H3 pakken
                    # dag = int(eerste twee letters)
                    # maand: opzoeken in dict
                    # jaar: int(laatste vier letters)
                    d = tree.xpath('//*[@class="content-main"]/h3/text()')[0].strip()
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
                    teaser = " ".join(tree.xpath('//*/p[@class="intro"]//text()'))
                except:
                    print("no teaser")
                    teaser = ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text = " ".join(tree.xpath('//*[@class="content-main"]//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                self.releases.append(
                    {
                        "text": text.strip(),
                        "title": title.strip(),
                        "teaser": teaser.strip(),
                        "date": datum,
                        "url": link.strip(),
                    }
                )
            except:
                print("no connection:\n" + link)

    def get(self, save):
        """                                                                             
        Fetches articles from Banco Santander Central Hispano
        """
        """ Grab the yearlinks from the actual/latest page """
        tree = fromstring(requests.get(self.START_URL).text)
        yearobjects = tree.xpath('//*/ul[@class="tab-header"]/li//a')
        year_links = [
            self.START_URL + l.attrib["href"] for l in yearobjects if "href" in l.attrib
        ]

        for year_link in year_links:
            tree = fromstring(requests.get(year_link).text)

            linkobjects = tree.xpath('//*[@class="annual-details"]/ul/li/p//a')
            links = [
                self.BASE_URL + l.attrib["href"]
                for l in linkobjects
                if "href" in l.attrib
            ]
            self.process_links(links)

        return self.releases
