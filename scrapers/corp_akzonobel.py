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

class akzonobel(Scraper):
    """Scrapes Akzo Nobel"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.akzonobel.com/media-releases-and-features"
        self.BASE_URL = "https://www.akzonobel.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Akzo Nobel
        '''
        self.doctype = "AkzoNobel (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)

        releases = []

        page = 0
        current_url = self.START_URL+'?page='+str(page)
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'No results found within the selected categories and filters') == -1:
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*[@class="teaser-media-release  theme-corporate"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*/h1[@class="title"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*/p[@class="maincontent-introduction"]//text()'))
                except:
                    teaser= ""
                teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="rich-text"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'teaser': teaser.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?page='+str(page)
            overview_page = requests.get(current_url)

        return releases