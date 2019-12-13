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


class dsm(Scraper):
    """Scrapes DSM"""

    def __init__(self):
        self.START_URL = "https://www.dsm.com/corporate/media/informationcenter-news."
        self.BASE_URL = "https://www.dsm.com/"
        self.doctype = "DSM (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=18)

    def get(self, save):
        """                                                                             
        Fetches articles from DSM
        """

        releases = []

        year = 2016
        current_url = (
            self.START_URL + "limit.10.markets.dsm.offset.0.year." + str(year) + ".html"
        )
        overview_page = requests.get(current_url)
        while overview_page.text.find("info-item clearfix collapsed") != -1:

            page = 0
            while overview_page.text.find("info-item clearfix collapsed") != -1:
                tree = fromstring(overview_page.text)

                linkobjects = tree.xpath("//h4//a")
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
                            tree.xpath('//*[@class="title subtitle"]/h1/text()')
                        )
                    except:
                        print("no title")
                        title = ""
                    try:
                        teaser = " ".join(
                            tree.xpath('//*/span[@class="intro"]//text()')
                        )
                    except:
                        teaser = ""
                        teaser_clean = " ".join(teaser.split())
                    try:
                        text = " ".join(
                            tree.xpath('//*[@class="text parbase section"]/p//text()')
                        )
                    except:
                        logger.info("oops - geen textrest?")
                        text = ""
                    text = "".join(text)
                    releases.append(
                        {
                            "text": text.strip(),
                            "title": title.strip(),
                            "teaser": teaser.strip(),
                            "url": link.strip(),
                        }
                    )

                page += 10
                current_url = (
                    self.START_URL
                    + "offset."
                    + str(page)
                    + ".year."
                    + str(year)
                    + ".limit.10.html"
                )
                overview_page = requests.get(current_url)

            year += 1
            current_url = (
                self.START_URL
                + "limit.10.markets.dsm.offset.0.year."
                + str(year)
                + ".html"
            )
            overview_page = requests.get(current_url)

        return releases
