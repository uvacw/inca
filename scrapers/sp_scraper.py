import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging
from time import sleep
from random import randrange
import json

logger = logging.getLogger(__name__)

class sp(Scraper):
    """Scrapes SP"""

    def __init__(self,database=True, maxpages = 2):
        '''
        maxpages = number of pages to scrape
        '''
        
        self.database = database
        self.START_URL = "https://www.sp.nl/nu/"
        self.BASE_URL = "https://www.sp.nl"
        self.MAXPAGES = maxpages

    def get(self):
        '''                                                                     
        Fetches articles from SP
        '''
        self.doctype = "SP (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=29)


        releases = []
        page=0
        current_url = self.START_URL+'js?page='+str(page)
        overview_page = requests.get(current_url, timeout = 10)
        while True:
            tree = json.loads(overview_page.text)
            if tree['has_pager'] is False:
                break
            if page > self.MAXPAGES:
                break
            elif page ==1:
                first_page_text=overview_page.text
            tree2 = tree['rendered_items']
            links = re.findall('href=\"(.*?)">',tree2)
            for link in links:
                full_link = self.BASE_URL + link
                logger.debug('ik ga nu {} ophalen'.format(full_link))
                try:
                    current_page = requests.get(full_link, timeout = 10)
                except requests.TooManyRedirects as e:
                    logger.debug("URL not working")
                    title = ""
                    publication_date = ""
                    text = ""
                    teaser = ""
                    continue
                current_page = requests.get(full_link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class = "h2 icon-title"]/text()'))
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    publication_date = "".join(tree.xpath('//*[@class ="date"]/text()'))
                except:
                    publication_date = ""

                try:
                    text = " ".join(tree.xpath('//*[@id = "content"]//p/text()|//*[@id = "content"]//p/em/text()|//*[@id = "content"]//p/a/text()')[1:]).strip()
                    text = text.replace('\n', '')
                except:
                    logger.debug("no text")
                    text = ""
                try:
                    teaser = "".join(tree.xpath('//*[@id = "content"]//p/text()|//*[@id = "content"]//p/em/text()|//*[@id = "content"]//p/a/text()')[0]).strip()
                    teaser = teaser.replace('\n', '')
                except:
                    teaser = ""
                try:
                    quote =  " ".join(tree.xpath('//*[@id = "content"]//blockquote/p/text()')).strip()
                except:
                    quote = ""
                releases.append({'text':text,
                                 'title':title,
                                 'publication_date': publication_date,
                                 'url':full_link,
                                 'teaser':teaser,
                                 'quote':quote})
            page+=1
            current_url = self.START_URL+'js?page='+str(page)
            overview_page=requests.get(current_url)

        return releases
            
