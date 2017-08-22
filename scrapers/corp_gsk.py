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

class gsk(Scraper):
    """Scrapes GlaxoSmithKline"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.gsk.com/en-gb/media/press-releases/"
        self.BASE_URL = "http://www.gsk.com/"

    def get(self):
        '''                                                                             
        Fetches articles from GSK
        '''
        self.doctype = "GSK (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

        releases = []

        page = 1
        current_url = self.START_URL+'/?p='+str(page)
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'Sorry, there are no search results.') == -1:
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*[@class="simple-listing__link"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="content-wrapper"]/h1/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class="intro"]/p//text()'))
                except:
                    teaser= ""
                teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="content-wrapper"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'teaser': teaser.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'/?p='+str(page)
            overview_page = requests.get(current_url)

        return releases