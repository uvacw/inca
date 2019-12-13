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


class pvv(Scraper):
    def __init__(self):

        self.START_URL = "https://www.pvv.nl/in-de-media/persberichten.html"
        self.BASE_URL = "https://www.pvv.nl"

    def get(self, save, maxpages, startpage, *args, **kwargs):
        """                                                                     
        Fetches articles from PVV
        maxpage = number of pages to scrape
        startpage: number of starting page for scraper (careful: must be divisable by 5)
        """
        self.doctype = "PVV (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)

        releases = []

        page = startpage
        current_url = self.START_URL
        overview_page = requests.get(current_url, timeout=10)
        first_page_text = ""
        while overview_page.text != first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > maxpages:
                break
            elif page == 1:
                first_page_text = overview_page.text
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@itemprop="name"]/a')
            links = [
                self.BASE_URL + l.attrib["href"]
                for l in linkobjects
                if "href" in l.attrib
            ]
            for link in links:
                logger.debug("ik ga nu {} ophalen".format(link))
                current_page = requests.get(link, timeout=10)
                tree = fromstring(current_page.text)
                try:
                    text = " ".join(
                        tree.xpath(
                            '//*[@itemprop = "articleBody"]/p/text()|//*[@itemprop = "articleBody"]/p/em/text()'
                        )
                    ).strip()
                except:
                    logger.debug("no text")
                    text = ""
                    text = "".join(text)
                try:
                    publication_date = "".join(
                        tree.xpath('//*[@class = "create"]/time/@datetime')
                    )
                    publication_date = publication_date[:-6]
                    publication_date = datetime.datetime.strptime(
                        publication_date, "%Y-%m-%dT%H:%M:%S"
                    )
                    publication_date = publication_date.date()
                except:
                    publication_date = None
                try:
                    ext_source = tree.xpath('//*[@itemprop="articleBody"]//@href')
                except:
                    ext_source = ""
                try:
                    title = "".join(
                        tree.xpath('//*[@itemprop = "headline"]/text()')
                    ).strip()
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    whole_release = " ".join(
                        tree.xpath(
                            '//*[@itemprop = "articleBody"]/p/text()|//*[@itemprop = "articleBody"]/p/em/text()|//*[@itemprop = "headline"]/text()'
                        )
                    ).strip()
                    whole_release = " ".join(whole_release.split())
                except:
                    whole_release = ""

                releases.append(
                    {
                        "text": text,
                        "title": title,
                        "publication_date": publication_date,
                        "url": link,
                        "ext_source": ext_source,
                        "whole_release": whole_release,
                    }
                )
            page += 5
            current_url = self.START_URL + "?start=" + str(page)
            overview_page = requests.get(current_url, timeout=10)

        return releases
