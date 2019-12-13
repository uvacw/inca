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


class bat(Scraper):
    """Scrapes British American Tobacco"""

    def __init__(self):
        self.START_URL = (
            "http://www.bat.com/group/sites/UK__9D9KCY.nsf/vwPagesWebLive/DO6YLKYF"
        )
        self.BASE_URL = "http://www.bat.com"

    def get(self, save):
        """                                                                             
        Fetches articles from British American Tobacco
        """
        self.doctype = "BAT (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=26)

        releases = []

        current_url = self.START_URL
        start_page = requests.get(current_url)
        tree = fromstring(start_page.text)
        yearobjects = tree.xpath('//*/ul[@class="ow_tabnav_ul"]//a')
        years = [
            self.BASE_URL + l.attrib["href"] for l in yearobjects if "href" in l.attrib
        ]

        for year in years:

            current_url = year
            year_page = requests.get(current_url)
            tree = fromstring(year_page.text)

            linkobjects = tree.xpath('//*[@class="stackRow"]//a[@class="link"]')
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
                    title = " ".join(tree.xpath('//*[@class="title"]/p/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    d = tree.xpath('//*[@class="standard gutterTop"]/p/strong//text()')[
                        0
                    ].strip()
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
                        tree.xpath('//*[@class="primaryContent gutterTop"]//text()')
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

        return releases
