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

class pvv(Scraper):
    """Scrapes PVV"""
    
    def __init__(self,database=True, maxpages = 2):
        '''
        maxpage = number of pages to scrape
        '''
        
        self.database = database
        self.START_URL = "https://www.pvv.nl/in-de-media/persberichten.html"
        self.BASE_URL = "https://www.pvv.nl"
        self.MAXPAGES = maxpages

    def get(self):
        '''                                                                     
        Fetches articles from PVV
        '''
        self.doctype = "PVV (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=29)

        releases = []

        page = 0
        current_url = self.START_URL
        overview_page = requests.get(current_url, timeout = 10)
        first_page_text=""
        while overview_page.text!=first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > self.MAXPAGES:
                break
            elif page ==1:
                first_page_text=overview_page.text
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@itemprop="name"]/a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link, timeout = 10)
                tree = fromstring(current_page.text)
                try:
                    text =" ".join(tree.xpath('//*[@itemprop = "articleBody"]/p/text()')).strip()
                except:
                    logger.debug("no text")
                    text=""
                    text="".join(text)
                try:
                    publication_date ="".join( tree.xpath('//*[@class = "create"]/time/@datetime'))
                    publication_date = publication_date[:-6]
                    publication_date = datetime.datetime.strptime(publication_date, '%Y-%m-%dT%H:%M:%S')
                    publication_date = publication_date.date()
                except:
                    publication_date=""
                try:
                    ext_source = tree.xpath('//*[@itemprop="articleBody"]//@href')
                except:
                    ext_source = ""
                try:
                    title ="".join( tree.xpath('//*[@itemprop = "headline"]/text()')).strip()
                except:
                    logger.debug("no title")
                    title = ""
                releases.append({'text':text,
                                 'title':title,
                                 'publication_date':publication_date,
                                 'url':link,
                                 'ext_source':ext_source,
                                 'html':current_page.text})
            page+=5
            current_url = self.START_URL+'?start='+str(page)
            overview_page=requests.get(current_url, timeout = 10)

        return releases


