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


class barclays(Scraper):
    """Scrapes Barclays"""

    def __init__(self):
        self.START_URL = "http://www.newsroom.barclays.com/Releases/ReleasesPage.aspx"
        self.BASE_URL = "http://www.newsroom.barclays.com/"
        self.current_year = 2017
        self.doctype = "Barclays (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=27)

    def get(self, save):
        """                                                                             
        Fetches articles from Barclays
        """

        releases = []

        year_to_process = 2006
        current_url = (
            self.START_URL + "?year_to_process=" + str(year_to_process)
            if year_to_process in range(2006, self.current_year)
            else self.START_URL
        )
        overview_page = requests.get(current_url)
        while overview_page.text.find("borderlist__item content") != -1:

            page = 1
            while overview_page.text.find("borderlist__item content") != -1:
                tree = fromstring(overview_page.text)

                linkobjects = tree.xpath(
                    '//*/article[@class="borderlist__item content"]//a'
                )
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
                            tree.xpath('//*/article[@class="release-detail"]/h1/text()')
                        )
                    except:
                        print("no title")
                        title = ""
                    try:
                        d = tree.xpath(
                            '//*/time[@id="MainContent_ReleaseText_dtreldate"]//text()'
                        )[0].strip()
                        jaar = int(d[-10:-6])
                        maand = MAAND2INT[d[2:-10].strip()]
                        dag = int(d[:2])
                        datum = datetime.datetime(jaar, maand, dag)
                    except Exception as e:
                        print("could not parse date")
                        print(e)
                        datum = None
                    try:
                        text = " ".join(tree.xpath('//*[@class="body"]//text()'))
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
                    self.START_URL
                    + "?year_to_process="
                    + str(year_to_process)
                    + "&pageNo="
                    + str(page)
                    if year_to_process in range(2006, self.current_year)
                    else self.START_URL + "?&pageNo=" + str(page)
                )
                overview_page = requests.get(current_url)

            year_to_process += 1
            if year_to_process > self.current_year:
                break
            current_url = (
                self.START_URL + "?year_to_process=" + str(year_to_process)
                if year_to_process in range(2006, self.current_year)
                else self.START_URL
            )
            overview_page = requests.get(current_url)

        return releases
