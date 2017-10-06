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

class lbg(Scraper):
    """Scrapes Lloyds Banking Group"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.lloydsbankinggroup.com/media/press-releases/"
        self.BASE_URL = "http://www.lloydsbankinggroup.com/"
        self.doctype = "LBG (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=27)

    def get(self):
        '''                                                                             
        Fetches articles from Lloyds Banking Group
        '''
        releases = []
        tree = fromstring(requests.get(self.START_URL).text)
        year_objects = tree.xpath('//*/nav[@class="right-nav hidden-xs"]/ul/li/ul/li//a')
        year_links = [self.BASE_URL+l.attrib['href'] for l in year_objects if 'href' in l.attrib]
        # print(year_links)

        for year_link in year_links:
            tree = fromstring(requests.get(year_link).text)
            lbg_object = tree.xpath('//*/nav[@class="right-nav hidden-xs"]/ul/li/ul/li/ul/li//a[@title="Lloyds Banking Group"]')
            lbg_link = [self.BASE_URL+l.attrib['href'] for l in lbg_object if 'href' in l.attrib]
            
            tree = fromstring(requests.get(lbg_link[0]).text)
            anchor_objects = tree.xpath('//*/ul[@class="recent-items-list"]/li//a[@class="arrow-link"]')
            anchor_links = [self.BASE_URL+l.attrib['href'] for l in anchor_objects if 'href' in l.attrib]

            for anchor_link in anchor_links:
                logger.debug('ik ga nu {} ophalen'.format(anchor_link))
                try:
                    tree = fromstring(requests.get(anchor_link).text)
                    try:
                        title=" ".join(tree.xpath('//*[@class="col-xs-12 col-sm-8 col-md-8"]/h1//text()'))
                    except:
                        print("no title")
                        title = ""
                    try:
                        text=" ".join(tree.xpath('//*[@class="rte"]/p//text()'))
                    except:
                        logger.info("oops - geen textrest?")
                        text = ""
                    text = "".join(text)
                    releases.append({'text':text.strip(),
                                     'title':title.strip(),
                                     'url':anchor_link.strip()})
                except:
                    print("no connection:\n" + anchor_link)

        return releases