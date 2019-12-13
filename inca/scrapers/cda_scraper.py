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


class cda(Scraper):
    """Scrapes CDA"""

    def __init__(self):
        self.START_URL = "https://www.cda.nl/actueel/nieuws"
        self.BASE_URL = "https://www.cda.nl"

    def get(self, save, maxpages, startpage, *args, **kwargs):
        """                                                                     
        Fetches articles from CDA
        maxpages: number of pages to scrape
        startpage: number of starting page for scraper
        """
        self.doctype = "CDA (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)

        logger.info("Scraping a maximum of {} pages".format(maxpages))
        releases = []

        page = startpage
        current_url = self.START_URL
        overview_page = requests.get(current_url)
        first_page_text = ""
        while overview_page.text != first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > maxpages:
                break
            elif page == 1:
                first_page_text = overview_page.text
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@class="panel panel--isLink"]')
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
                    title = "".join(
                        tree.xpath(
                            '//*[@class = "pageHeader-content"]//h1/span/text()|//*[@class ="widePhoto-content"]//h1/span/text()'
                        )
                    ).strip()
                except:
                    logger.debug("no title")
                    title = ""

                try:
                    text = "".join(
                        tree.xpath(
                            '//*[@id = "mainContent"]//div[@class = "mg-text-container"]/p/text()'
                        )
                    ).strip()
                    text = text.replace("\r", "")
                    text = text.replace("\xa0", "")
                except:
                    logger.info("no text?")
                    text = ""
                try:
                    publication_list = tree.xpath(
                        '//*[@class = "h5 paddedText-text u-background--blue u-color--white"]/text()'
                    )
                    newlist = []
                    for item in publication_list:
                        if item.strip() != "Actueel":
                            newlist.append(item)
                        else:
                            pass
                    publication_date = "".join(newlist).strip()
                    MAAND2INT = {
                        "januari": 1,
                        "februari": 2,
                        "maart": 3,
                        "april": 4,
                        "mei": 5,
                        "juni": 6,
                        "juli": 7,
                        "augustus": 8,
                        "september": 9,
                        "oktober": 10,
                        "november": 11,
                        "december": 12,
                    }
                    dag = publication_date[:2]
                    jaar = publication_date[-4:]
                    maand = publication_date[2:-4].strip().lower()
                    publication_date = datetime.datetime(
                        int(jaar), int(MAAND2INT[maand]), int(dag)
                    )
                    publication_date = publication_date.date()
                except:
                    publication_date = None
                try:
                    whole_release = "".join(
                        tree.xpath(
                            '//*[@class = "pageHeader-content"]//h1/span/text()|//*[@class ="widePhoto-content"]//h1/span/text()|//*[@id = "mainContent"]//div[@class = "mg-text-container"]/p/text()'
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
                        "whole_release": whole_release,
                    }
                )
            page += 1
            current_url = self.START_URL + "?lookup[page-7430]=" + str(page)
            overview_page = requests.get(current_url)

        return releases
