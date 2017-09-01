# DOESN'T WORK PROPERLY

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

class endesa(Scraper):
    """Scrapes Endesa"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.endesa.com/en/press/the-news.html"
        self.BASE_URL = "https://www.endesa.com"
        self.doctype = "Endesa (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=18)

    def get(self):
        '''                                                                             
        Fetches articles from Endesa
        '''

        releases = []

        page = 1
        current_url = self.START_URL+'#/page_'+str(page)
        overview_page = requests.get(current_url)
        first_page_text = ''
        while overview_page.text != first_page_text:

            if page == 1:
                first_page_text = overview_page.text
            
            tree = fromstring(overview_page.text)
            print(overview_page.text[:200])
            with open('testoverview.html',mode='w') as fo:
                fo.write(overview_page.text)
    
            linkobjects = tree.xpath('//*/h3[@class="list-item_title text--list-title-large"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            print(links)
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*/h1[@class="hero_title text--page-heading"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser="".join(tree.xpath('//*[@class="rich-text_inner"]/ul//text()')).strip()
                except:
                    teaser= ""
                teaser = " ".join(teaser.split())              
                try:
                    text=" ".join(tree.xpath('//*[@class="rich-text_inner"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'teaser':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'#/page_'+str(page)
            overview_page = requests.get(current_url)

        return releases