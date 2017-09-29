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

class pvda(Scraper):
    """Scrapes PvdA"""
    
    def __init__(self,database=True, maxpages = 2):
        '''
        maxpages = number of pages to scrape
        '''
        
        self.database = database
        self.START_URL = "https://www.pvda.nl/nieuws/"
        self.BASE_URL = "https://www.pvda.nl"

    def get(self):
        '''                                                                     
        Fetches articles from PvdA
        '''
        self.doctype = "PvdA (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=29)

        releases = []

        page = 1
        current_url = self.START_URL
        overview_page = requests.get(current_url)
        first_page_text=""
        while overview_page.text!=first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > self.MAXPAGES:
                break
            elif page ==1:
                first_page_text=overview_page.text
            tree = fromstring(overview_page.text)
            links = tree.xpath('//*[@id="content"]//h2/a/@href')
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class = "has-header"]//h1/text()'))
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    publication_date = "".join(tree.xpath('//*[@class ="meta"]/text()[2]'))
                    publication_date = publication_date[3:]
                except:
                    publication_date = ""

                try:
                    text = " ".join(tree.xpath('//*[@class = "content"]//p[not(@class="meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/text()|//*[@class = "content"]//p[not(@class ="meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/em/text()|//*[@class = "content"]//p[not(@class = "meta")and not(@class = "subtitle")and not(ancestor::blockquote)]/u/text()')).strip()
                    text = text.replace('\xa0', '')
                except:
                    logger.debug("no text")
                    text = ""
                try:
                    teaser = "".join(tree.xpath('//*[@class = "content"]/div[not(@class ="related-excerpt")]/h2/text()|//*[@class = "content"]/div[not(@class ="related-excerpt")]/h3/text()')[0]).strip()
                except:
                    teaser = ""
                try:
                    quote = "".join(tree.xpath('//*[@class = "content"]//blockquote/p/text()')).strip()
                except:
                    quote = ""
                                     
                releases.append({'text':text,
                                 'title':title,
                                 'publication_date': publication_date,
                                 'url':link,
                                 'teaser':teaser,
                                 'quote':quote})
            page+=1
            current_url = self.START_URL+'page/'+str(page)
            overview_page=requests.get(current_url)

        return releases                    
                    
