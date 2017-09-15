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

class compass(Scraper):
    """Scrapes Compass Group"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.compass-group.com/en/media/news.html"
        self.BASE_URL = "https://www.compass-group.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Compass Group
        '''
        self.doctype = "Compass (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=26)

        releases = []

        year = 2012
        current_url = self.START_URL+'?tab1='+str(year)
        overview_page = requests.get(current_url)
        while overview_page.text.find('list-item list-item-even') != -1:
            
            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*/p[@class="article-list-item-date"]//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="default"]/h2/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="default"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            year+=1
            current_url = self.START_URL+'?tab1='+str(year)
            overview_page = requests.get(current_url)

        return releases