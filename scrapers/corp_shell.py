import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

class shell(Scraper):
    """Scrapes Shell"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.shell.com/media/news-and-media-releases.html"
        self.BASE_URL = "http://www.shell.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Shell
        '''
        self.doctype = "shell (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)

        releases = []

        overview_page = requests.get(self.START_URL)
        tree = fromstring(overview_page.text)

        linkobjects = tree.xpath('//h3//a')
        links = [self.BASE_URL+l.attrib['href'] for l in linkobjects]

        for link in links: 
            logger.debug('ik ga nu {} ophalen'.format(link))
            current_page = requests.get(link)
            tree = fromstring(current_page.text)
            try:
                title=" ".join(tree.xpath('//*[@class="page-header__header"]/h1/text()'))
            except:
                print("no title")
                title = ""
            try:
                teaser=" ".join(tree.xpath('//*[@class="page-header__text"]/p//text()'))
            except:
                teaser= ""
                teaser_clean = " ".join(teaser.split())
            try:
                text=" ".join(tree.xpath('//*[@class="text-image__text"]//text()'))
            except:
                logger.info("oops - geen textrest?")
                text = ""
            text = "".join(text)
            releases.append({'text':text.strip(),
                             'teaser': teaser.strip(),
                             'title':title.strip(),
                             'url':link.strip()})

        return releases