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

class sbm(Scraper):
    """Scrapes SBM Offshore 2013-present"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.sbmoffshore.com/investor-relations-centre/press-releases/"
        self.BASE_URL = "http://www.sbmoffshore.com/"

    def get(self):
        '''                                                                             
        Fetches articles from SBM Offshore
        '''
        self.doctype = "SBMOffshore (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=11)

        releases = []

        year = 2013
        current_url = self.START_URL+'?y='+str(year)
        overview_page = requests.get(current_url)
        while overview_page.text.find('single-release') != -1:

            page = 1
            while overview_page.text.find('single-release') != -1:
                tree = fromstring(overview_page.text)
        
                linkobjects = tree.xpath('//*/h2[@class="release-title"]//a')
                links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
                
                for link in links:
                    logger.debug('ik ga nu {} ophalen'.format(link))
                    current_page = requests.get(link)
                    tree = fromstring(current_page.text)
                    try:
                        title=" ".join(tree.xpath('//*/h1[@class="entry-title"]/text()'))
                    except:
                        print("no title")
                        title = ""
                    try:
                        text=" ".join(tree.xpath('//*[@class="entry-content top-padding "]//text()'))
                    except:
                        logger.info("oops - geen textrest?")
                        text = ""
                    text = "".join(text)
                    releases.append({'text':text.strip(),
                                     'title':title.strip(),
                                     'url':link.strip()})

                page+=1
                current_url = self.START_URL+'page/'+str(page)+'/?y='+str(year)
                overview_page = requests.get(current_url)

            year+=1
            current_url = self.START_URL+'?y='+str(year)
            overview_page = requests.get(current_url)

        return releases