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

class aegon(Scraper):
    """Scrapes aegon"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.aegon.com/en/Home/Investors/News-releases/"
        self.BASE_URL = "https://www.aegon.com/"
        self.doctype = "aegon (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)
   
    def get(self):
        '''                                                                             
        Fetches articles from Aegon
        '''

        releases = []
        tree = fromstring(requests.get(self.START_URL).text)

        linkobjects = tree.xpath('//*[@class="overviewpage-section"][1]/div/div/h4[@class="item-header"]//a')
        links = [self.BASE_URL+l.attrib['href'] for l in linkobjects]

        for link in links: 
            logger.debug('ik ga nu {} ophalen'.format(link))
            tree = fromstring(requests.get(link).text)
            try:
                title="".join(tree.xpath('//*[@class="header-container"]/h1//text() | //*[@class="header-container lang-switch-single"]/h1//text()')).strip()
            except:
                print("no title")
                title = ""
            try:
                teaser="".join(tree.xpath('//*[@class="aeg-intro"]/p//text()')).strip()
            except:
                print("no teaser")
                teaser= ""
                teaser_clean = " ".join(teaser.split())
            try:
                text="".join(tree.xpath('//*[@class="aeg-xhtml-content"]//text()')).strip()
            except:
                print("geen text")
                logger.info("oops - geen textrest?")
                text = ""
            text = "".join(text)
            releases.append({"title":title.strip(),
                           "teaser":teaser.strip(),
                           "text":text.strip()
                           })

        return releases