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
import time
import random

logger = logging.getLogger(__name__)

class amadeus(Scraper):
    """Scrapes Amadeus IT Group SA"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.amadeus.com/web/amadeus/en_US-US/Amadeus-Home/News-and-events/News/"
        self.BASE_URL = "http://www.amadeus.com/"
        self.doctype = "Amadeus (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=21)

    def get(self):
        '''                                                                             
        Fetches articles from Amadeus IT Group SA
        '''

        releases = []

        page = 1
        current_url = self.START_URL+'1259071352352-Page-AMAD_NewsPpal?business=1259067571417&financial=1259067571427&np='+str(page)+'&result=1259068355670%2C1259110055779%2C1259068355704%2C1319653601062%2C1259068355719%2C1259068355734%2C1259068355747%2C1259068355760%2C1259068355689%2C1259068355773%2C1259068355786%2C1319608908790%2C1259068355799%2C1259068355812%2C1259068355825%2C1319609075305&years=2017%2C2016%2C2015%2C2014%2C2013%2C2012%2C2011%2C2010%2C2009%2C2008%2C2007%2C2006'
        overview_page = requests.get(current_url)
        while overview_page.text.find('first item') != -1:
            tree = fromstring(overview_page.text)
        
            linkobjects = tree.xpath('//*/ul[@class="list news-list"]//li//h2//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            print(links)
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="main col3"]/h1/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class="intro"]/h1//text()'))
                except:
                    print("no teaser")
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="intro"]/div/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'teaser':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            # If you try to download more than 2 or 3 pages, you get a HTTP-503 (service unavailable)
            # Tried to solve it with random sleep, but that's not enough.
            # Probably can only be solved by scraping with different IPs/different days/different user agent/... (to be determiend)
            time.sleep(random.randrange(5,10))
            current_url = self.START_URL+'1259071352352-Page-AMAD_NewsPpal?business=1259067571417&financial=1259067571427&np='+str(page)+'&result=1259068355670%2C1259110055779%2C1259068355704%2C1319653601062%2C1259068355719%2C1259068355734%2C1259068355747%2C1259068355760%2C1259068355689%2C1259068355773%2C1259068355786%2C1319608908790%2C1259068355799%2C1259068355812%2C1259068355825%2C1319609075305&years=2017%2C2016%2C2015%2C2014%2C2013%2C2012%2C2011%2C2010%2C2009%2C2008%2C2007%2C2006'
            overview_page = requests.get(current_url)
            with open('test_{}.html'.format(page),mode='w') as fo:
                fo.write(overview_page.text)

        return releases