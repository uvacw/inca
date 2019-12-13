import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging
from time import sleep
from random import randrange
import json

logger = logging.getLogger("INCA")


class sp(Scraper):
    """Scrapes SP"""

    def __init__(self):

        self.START_URL = "http://www.sp.nl/nu/"
        self.BASE_URL = "http://www.sp.nl"

    def get(self, save, maxpages, startpage, *args, **kwargs):
        """                                                                     
        Fetches articles from SP
        maxpages = number of pages to scrape
        startpage: number of starting page for scraper
        """
        self.doctype = "SP (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)

        releases = []
        page = startpage
        current_url = self.START_URL + "js?page=" + str(page)
        overview_page = requests.get(current_url, timeout=10)
        while True:
            tree = json.loads(overview_page.text)
            if tree["has_pager"] is False:
                break
            if page > maxpages:
                break
            elif page == 1:
                first_page_text = overview_page.text
            tree2 = tree["rendered_items"]
            links = re.findall('href="(.*?)">', tree2)
            for link in links:
                full_link = self.BASE_URL + link
                logger.debug("ik ga nu {} ophalen".format(full_link))
                try:
                    current_page = requests.get(full_link, timeout=10)
                except requests.TooManyRedirects as e:
                    logger.debug("URL not working")
                    title = ""
                    publication_date = ""
                    text = ""
                    teaser = ""
                    continue
                current_page = requests.get(full_link)
                tree = fromstring(current_page.text)
                try:
                    title = " ".join(tree.xpath('//*[@class = "h2 icon-title"]/text()'))
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    publication_date = "".join(tree.xpath('//*[@class ="date"]/text()'))
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
                    text = " ".join(
                        tree.xpath(
                            '//*[@id = "content"]//p/text()|//*[@id = "content"]//p/em/text()|//*[@id = "content"]//p/a/text()'
                        )[1:]
                    ).strip()
                    text = text.replace("\n", "")
                    text = text.replace("\xa0", "")
                except:
                    logger.debug("no text")
                    text = ""
                try:
                    teaser = "".join(
                        tree.xpath(
                            '//*[@id = "content"]//p/text()|//*[@id = "content"]//p/em/text()|//*[@id = "content"]//p/a/text()'
                        )[0]
                    ).strip()
                    teaser = teaser.replace("\n", "")
                    teaser = teaser.replace("\xa0", "")
                except:
                    teaser = ""
                try:
                    quote = " ".join(
                        tree.xpath('//*[@id = "content"]//blockquote/p/text()')
                    ).strip()
                except:
                    quote = ""
                try:
                    whole_release = " ".join(
                        tree.xpath(
                            '//*[@class = "h2 icon-title"]/text()|//*[@id = "content"]//p/text()|//*[@id = "content"]//p/em/text()|//*[@id = "content"]//p/a/text()|//*[@id = "content"]//blockquote/p/text()'
                        )
                    ).strip()

                    whole_release = whole_release.replace("\n", "")
                    whole_release = whole_release.replace("\xa0", "")
                    whole_release = whole_release.replace("\t", "")
                except:
                    whole_release = ""

                releases.append(
                    {
                        "text": text,
                        "title": title,
                        "publication_date": publication_date,
                        "url": full_link,
                        "teaser": teaser,
                        "quote": quote,
                        "whole_release": whole_release,
                    }
                )
            page += 1
            current_url = self.START_URL + "js?page=" + str(page)
            overview_page = requests.get(current_url)

        return releases
