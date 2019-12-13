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


class pvda(Scraper):
    """Scrapes PvdA"""

    def __init__(self):

        self.START_URL = "https://www.pvda.nl/nieuws/"
        self.BASE_URL = "https://www.pvda.nl"

    def get(self, save, maxpages, startpage, *args, **kwargs):
        """                                                                     
        Fetches articles from PvdA
        maxpages = number of pages to scrape
        startpage: number of starting page for scraper
        """
        self.doctype = "PvdA (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)

        releases = []

        page = startpage
        current_url = self.START_URL + "page/" + str(page)
        overview_page = requests.get(current_url)
        first_page_text = ""
        while overview_page.text != first_page_text:
            logger.debug("Now fetching overview page {}".format(page))
            if page > maxpages:
                break
            elif page == 1:
                first_page_text = overview_page.text
            tree = fromstring(overview_page.text)
            links = tree.xpath('//*[@id="content"]//h2/a/@href')
            for link in links:
                logger.debug("ik ga nu {} ophalen".format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title = " ".join(
                        tree.xpath('//*[@class = "has-header"]//h1/text()')
                    )
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    publication_list = tree.xpath('//*[@class ="meta"]/text()')
                    newlist = []
                    for item in publication_list:
                        if item != " Door " and item != ", ":
                            newlist.append(item)
                        else:
                            pass
                    publication_date = "".join(newlist)
                    publication_date = publication_date[4:].strip()
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
                            '//*[@class = "content"]//p[not(@class="meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/text()|//*[@class = "content"]//p[not(@class ="meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/em/text()|//*[@class = "content"]//p[not(@class = "meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/u/text()|//*[@class = "bumpedFont15"]/text()'
                        )
                    ).strip()
                    text = text.replace("\xa0", "")
                    text = " ".join(text.split())
                except:
                    logger.debug("no text")
                    text = ""
                try:
                    teaser = "".join(
                        tree.xpath(
                            '//*[@class = "content"]/div[not(@class ="related-excerpt")]/h2/text()|//*[@class = "content"]/div[not(@class ="related-excerpt")]/h3/text()'
                        )[0]
                    ).strip()
                except:
                    teaser = ""
                try:
                    quote = "".join(
                        tree.xpath('//*[@class = "content"]//blockquote/p/text()')
                    ).strip()
                except:
                    quote = ""
                try:
                    whole_release = " ".join(
                        tree.xpath(
                            '//*[@class = "has-header"]//h1/text()|//*[@class = "content"]//p[not(@class="meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/text()|//*[@class = "content"]//p[not(@class ="meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/em/text()|//*[@class = "content"]//p[not(@class = "meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/u/text()|//*[@class = "bumpedFont15"]/text()|//*[@class = "content"]/div[not(@class ="related-excerpt")]/h2/text()|//*[@class = "content"]/div[not(@class ="related-excerpt")]/h3/text()|//*[@class = "content"]//blockquote/p/text()'
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
                        "teaser": teaser,
                        "quote": quote,
                        "whole_release": whole_release,
                    }
                )
            page += 1
            current_url = self.START_URL + "page/" + str(page)
            overview_page = requests.get(current_url)

        return releases
