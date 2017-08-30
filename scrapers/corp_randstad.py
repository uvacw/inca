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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)
driver = webdriver.PhantomJS()
timeout = 10

class randstad(Scraper):
    """Randstad"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.ir.randstad.com/news-and-events/press-releases.aspx"
        self.BASE_URL = "https://www.ir.randstad.com"
        self.doctype = "Randstad"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=16)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug('ik ga nu {} ophalen'.format(link))
            try:
                tree = fromstring(requests.get(self.BASE_URL + link).text)
                try:
                    title=" ".join(tree.xpath('//*[@class="pr-Title"]/h2/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="pr-Content"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                self.releases.append({'text':text.strip(),
                                      'title':title.strip(),
                                      'url':link.strip()})
            except:
                print("no connection:\n" + link)

    def get(self):
        '''                                                                             
        Fetches articles from Randstad
        '''
        driver = webdriver.PhantomJS()
        timeout = 10

        try:
            driver.get("https://www.ir.randstad.com/news-and-events/press-releases.aspx?page=1")
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        
            tree = fromstring(driver.page_source)
            linkobjects = tree.xpath('//*[@class="press-title"]//a')
            links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            print('\n'.join(links))
            self.process_links(links)
            
            button_right = driver.find_element_by_class_name("pagenav").find_elements_by_tag_name("a")[-2].get_attribute("href")
            while button_right != "javascript:":
                driver.get(button_right)
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        
                tree = fromstring(driver.page_source)
                linkobjects = tree.xpath('//*[@class="press-title"]//a')
                links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
                print('\n'.join(links))
                self.process_links(links)
                button_right = driver.find_element_by_class_name("pagenav").find_elements_by_tag_name("a")[-2].get_attribute("href")
        except Exception as e:
            print("Exception:" + str(e))

        driver.quit()

        return self.releases