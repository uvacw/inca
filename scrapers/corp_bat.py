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

class bat(Scraper):
    """Scrapes British American Tobacco"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.bat.com/group/sites/UK__9D9KCY.nsf/vwPagesWebLive/DO6YLKYF"
        self.BASE_URL = "http://www.bat.com"

    def get(self):
        '''                                                                             
        Fetches articles from British American Tobacco
        '''
        self.doctype = "BAT (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=26)

        releases = []

        current_url = self.START_URL
        start_page = requests.get(current_url)
        tree = fromstring(start_page.text)
        yearobjects = tree.xpath('//*/ul[@class="ow_tabnav_ul"]//a')
        years = [self.BASE_URL+l.attrib['href'] for l in yearobjects if 'href' in l.attrib]
        
        for year in years:

            current_url = year
            year_page = requests.get(current_url)
            tree = fromstring(year_page.text)
    
            linkobjects = tree.xpath('//*[@class="stackRow"]//a[@class="link"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="title"]/p/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="primaryContent gutterTop"]//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})#

        return releases