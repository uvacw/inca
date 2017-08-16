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

class wolters(Scraper):
    """Scrapes Wolters Kluwer"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://wolterskluwer.com/company/newsroom/news"
        self.BASE_URL = "https://www.wolterskluwer.com/"
        self.doctype = "Wolters (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=18)

    def get(self):
        '''                                                                             
        Fetches articles from Wolters Kluwer
        '''

        releases = []

        page = 1
        current_url = self.START_URL+'?r41_r1:pageSize=5&r41_r1:page='+str(page)
        overview_page = requests.get(current_url)
        first_page_text = ''
        while overview_page.text != first_page_text:

            if page == 1:
                first_page_text = overview_page.text
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*[@class="newsFilterResult_title"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*/h1[@class="article_title"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="article_content"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?r41_r1:pageSize=5&r41_r1:page='+str(page)
            overview_page = requests.get(current_url)

        return releases