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

class mapfre(Scraper):
    """Scrapes Mapfre"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://noticias.mapfre.com/en/category/news-corporate/"
        self.BASE_URL = "https://noticias.mapfre.com/"
        self.doctype = "Mapfre (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)

    def get(self):
        '''                                                                             
        Fetches articles from Mapfre
        '''

        releases = []

        page = 1
        current_url = self.START_URL+'page/'+str(page)+'/'
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'Oops, This Page Could Not Be Found!') == -1:
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*/h2[@class="entry-title fusion-post-title"]//a')
            links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*/h2[@class="entry-title fusion-post-title"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser="".join(tree.xpath('//*[@class="post-content"]/p/strong//text()')).strip()
                except:
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="post-content"]//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'teaser':teaser.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'page/'+str(page)+'/'
            overview_page = requests.get(current_url)

        return releases