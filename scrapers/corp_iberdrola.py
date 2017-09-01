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

class iberdrola(Scraper):
    """Scrapes Iberdrola"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.iberdrola.com/press-room/news/"
        self.BASE_URL = "https://www.iberdrola.com"
        self.doctype = "Iberdrola (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=21)
        
    def get(self):
        '''                                                                             
        Fetches articles from Iberdrola
        '''

        releases = []

        page = 1
        current_url = self.START_URL+'pag-'+str(page)+'/'
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'we have not found results according to your search') == -1:
            
            tree = fromstring(overview_page.text)

            #with open('test.html',mode='w') as fo:
            #    fo.write(overview_page.text)
    
            linkobjects = tree.xpath('//*/li[@class="resultado"]//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="tituloNoticia"]/h1//text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser="".join(tree.xpath('//*/p[@class="antetitulo"]//text()')).strip()
                except:
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="bulletsNoticia"]/ul/li//text() | //*[@class="noticia"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'teaser':teaser.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'pag-'+str(page)+'/'
            overview_page = requests.get(current_url)

        return releases