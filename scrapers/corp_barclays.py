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

class barclays(Scraper):
    """Scrapes Barclays"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.newsroom.barclays.com/Releases/ReleasesPage.aspx"
        self.BASE_URL = "http://www.newsroom.barclays.com/"
        self.current_year = 2017

    def get(self):
        '''                                                                             
        Fetches articles from Barclays
        '''
        self.doctype = "Barclays (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=27)

        releases = []

        year_to_process = 2006
        current_url = self.START_URL+'?year_to_process='+str(year_to_process) if year_to_process in range(2006, self.current_year) else self.START_URL
        overview_page = requests.get(current_url)
        while overview_page.text.find('borderlist__item content') != -1:

            page = 1
            while overview_page.text.find('borderlist__item content') != -1:
                tree = fromstring(overview_page.text)
                
                linkobjects = tree.xpath('//*/article[@class="borderlist__item content"]//a')
                links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
                
                for link in links:
                    logger.debug('ik ga nu {} ophalen'.format(link))
                    current_page = requests.get(link)
                    tree = fromstring(current_page.text)
                    try:
                        title=" ".join(tree.xpath('//*/article[@class="release-detail"]/h1/text()'))
        #                print("this prints title", title)
                    except:
                        print("no title")
                        title = ""
                    try:
                        text=" ".join(tree.xpath('//*[@class="body"]//text()'))
                    except:
        #           print("geen text")
                        logger.info("oops - geen textrest?")
                        text = ""
                    text = "".join(text)
                    releases.append({'text':text.strip(),
                                     'title':title.strip(),
                                     'url':link.strip()})

                page+=1
                current_url = self.START_URL+'?year_to_process='+str(year_to_process)+'&pageNo='+str(page) if year_to_process in range(2006, self.current_year) else self.START_URL+'?&pageNo='+str(page)
                overview_page = requests.get(current_url)

            year_to_process+=1
            if year_to_process > self.current_year: break
            current_url = self.START_URL+'?year_to_process='+str(year_to_process) if year_to_process in range(2006, self.current_year) else self.START_URL
            overview_page = requests.get(current_url)

        return releases
