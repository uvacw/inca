# http://phantomjs.org/download.html
# https://chromedriver.storage.googleapis.com/index.html?path=2.31/
# pip install selenium
# driver = webdriver.Chrome()
# import time

import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging
import time
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("INCA")
timeout = 10
MAAND2INT = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


class randstad(Scraper):
    """Randstad"""

    def __init__(self):
        self.START_URL = (
            "https://www.ir.randstad.com/news-and-events/press-releases.aspx"
        )
        self.BASE_URL = "https://www.ir.randstad.com"
        self.doctype = "Randstad"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=16)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            try:
                tree = fromstring(requests.get(self.BASE_URL + link).text)
                try:
                    title = " ".join(tree.xpath('//*[@class="pr-Title"]/h2/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    d = tree.xpath('//*[@class="pr-Content"]/p/text()')[0].strip()
                    print(d)
                    jaar = int(d[-4:])
                    maand = MAAND2INT[d[2:-4].strip()]
                    dag = int(d[:2])
                    datum = datetime.datetime(jaar, maand, dag)
                except Exception as e:
                    print("could not parse date")
                    print(e)
                    datum = None
                try:
                    text = " ".join(tree.xpath('//*[@class="pr-Content"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                self.releases.append(
                    {
                        "text": text.strip(),
                        "date": datum,
                        "title": title.strip(),
                        "url": link.strip(),
                    }
                )
            except:
                print("no connection:\n" + link)

    def get(self, save):
        """                                                                             
        Fetches articles from Randstad
        """
        try:
            driver = webdriver.PhantomJS()
        except selenium.common.exceptions.WebDriverException:
            logger.critical(
                "Unable to run Randstad scraper, no PhantomJS in path. Try (re)installing PhantomJS."
            )
            return []
        timeout = 10

        try:
            driver.get(
                "https://www.ir.randstad.com/news-and-events/press-releases.aspx?page=1"
            )
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "html"))
            )

            tree = fromstring(driver.page_source)
            linkobjects = tree.xpath('//*[@class="press-title"]//a')
            links = [l.attrib["href"] for l in linkobjects if "href" in l.attrib]
            print("\n".join(links))
            self.process_links(links)

            button_right = (
                driver.find_element_by_class_name("pagenav")
                .find_elements_by_tag_name("a")[-2]
                .get_attribute("href")
            )
            while button_right != "javascript:":
                driver.get(button_right)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "html"))
                )

                tree = fromstring(driver.page_source)
                linkobjects = tree.xpath('//*[@class="press-title"]//a')
                links = [l.attrib["href"] for l in linkobjects if "href" in l.attrib]
                print("\n".join(links))
                self.process_links(links)
                button_right = (
                    driver.find_element_by_class_name("pagenav")
                    .find_elements_by_tag_name("a")[-2]
                    .get_attribute("href")
                )
        except Exception as e:
            print("Exception:" + str(e))

        driver.quit()

        return self.releases
