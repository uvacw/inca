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

class bhp(Scraper):
    """Scrapes BHP Billiton"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.bhp.com/media-and-insights/news-releases"
        self.BASE_URL = "http://www.bhp.com/"

    def get(self):
        '''                                                                             
        Fetches articles from BHP Billiton
        '''
        self.doctype = "BHP (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=26)

        releases = []

        page = 0
        current_url = self.START_URL+'?q0='+str(page)
        overview_page = requests.get(current_url)
        while overview_page.text.find('listing__item-wrap') != -1:
            
            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*[@class="col-9"]/h2//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="col-9 col-r"]/h2/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="rte col-12"]//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?q0='+str(page)
            overview_page = requests.get(current_url)

        return releases