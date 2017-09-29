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

class cda(Scraper):
    """Scrapes CDA"""

    def __init__(self,database=True, maxpages = 2):
        '''
        maxpages = number of pages to scrape
        '''
        self.database = database
        self.START_URL = "https://www.cda.nl/actueel/nieuws"
        self.BASE_URL = "https://www.cda.nl"
        self.MAXPAGES = maxpages

    def get(self):
        '''                                                                     
        Fetches articles from CDA
        '''
        self.doctype = "CDA (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=25)
        

        releases = []

        page = 0
        current_url = self.START_URL
        overview_page = requests.get(current_url)
        first_page_text = ""
        while overview_page.text!=first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > self.MAXPAGES:
                break
            elif page ==1:
                first_page_text=overview_page.text
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@class="panel panel--isLink"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link, timeout = 10)
                tree = fromstring(current_page.text)
                try:
                    title= "".join(tree.xpath('//*[@class = "pageHeader-content"]//h1/span/text()|//*[@class ="widePhoto-content"]//h1/span/text()')).strip()
                except:
                    logger.debug("no title")
                    title = ""

                try:
                    text="".join(tree.xpath('//*[@id = "mainContent"]//div[@class = "mg-text-container"]/p/text()')).strip()
                    text=text.replace('\r', '')
                    text=text.replace('\xa0', '')
                except:
                    logger.info("no text?")
                    text =""
                try:
                    publication_date  = "".join(tree.xpath('//*[@class = "h5 paddedText-text u-background--blue u-color--white"]/text()')).strip()
                    publication_date = datetime.datetime.strptime(publication_date, '%d %B %Y')
                    publication_date = publication_date.date()
                except:
                    publication_date = ""

                releases.append({'text':text,
                                 'title':title,
                                 'publication_date':publication_date,
                                 'url':link})
            page+=1
            current_url = self.START_URL+'?lookup[page-7430]='+str(page)
            overview_page=requests.get(current_url)

        return releases
			
