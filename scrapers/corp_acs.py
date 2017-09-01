# DOESN'T WORK PROPERLY

# http://phantomjs.org/download.html
# https://chromedriver.storage.googleapis.com/index.html?path=2.31/
# pip install selenium
# driver = webdriver.Chrome()
# import time

import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging
from selenium import webdriver
import time

logger = logging.getLogger(__name__)

class acs(Scraper):
    """Scrapes Actividades de Construccion y Servicios"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.grupoacs.com/site/index?url=press-room%2Fnews%2Fpress-releases%2F&page=1"
        self.BASE_URL = "http://www.grupoacs.com/"
        self.doctype = "ACS"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=21)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug('ik ga nu {} ophalen'.format(link))
            try:
                tree = fromstring(requests.get(self.BASE_URL + link).text)
                try:
                    title=" ".join(tree.xpath('//*[@class="col-md-8 prensa-titulo"]/h3/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    teaser="".join(tree.xpath('//*[@class="col-md-8 prensa-subtitulo"]/p//text()')).strip()
                except:
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="col-md-12"]//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                self.releases.append({'text':text.strip(),
                                      'title':title.strip(),
                                      'teaser':teaser.strip(),
                                      'url':link.strip()})
            except:
                print("no connection:\n" + link)

    def get(self):
        '''                                                                             
        Fetches articles from ACS
        '''
        driver = webdriver.PhantomJS()
        driver.get(self.START_URL)
        time.sleep(2)
        # don't ask me why but driver.page_source must explicitly be referenced
        # before continuing
        dummy_page_source = driver.page_source
        tree = fromstring(driver.page_source)

        linkobjects = tree.xpath('//*[@class="col-md-10"]//a')
        links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
        print('\n'.join(links))
        self.process_links(links)
    
        try:
            button_right = driver.find_element_by_class_name("next")
            while button_right.get_attribute("class").find("next disabled") == -1:
                
                # this doesn't work, because apparently clicking does not lead to the next page
                # even though the element is correctly identified
                button_right.click()
                time.sleep(5)
                # processing here
                tree = fromstring(driver.getPageSource())

                linkobjects = tree.xpath('//*[@class="col-md-10"]//a')
                links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
                print('\n'.join(links))
                self.process_links(links)

                button_right = driver.find_element_by_class_name("next")
        except:
            print('Error occurred.')

        driver.quit()
        return self.releases