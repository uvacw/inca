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
import selenium
from selenium import webdriver
import time

logger = logging.getLogger("INCA")


class kpn(Scraper):
    """Scrapes KPN"""

    def __init__(self):
        self.START_URL = "http://corporate.kpn.com/press/press-releases.htm"
        self.BASE_URL = "http://corporate.kpn.com/"
        self.doctype = "KPN"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            try:
                tree = fromstring(requests.get(self.BASE_URL + link).text)
                try:
                    title = " ".join(tree.xpath('//*/h2[@class="article"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text = " ".join(
                        tree.xpath(
                            '//*/article[@class="kpn-article kpn-collapsible-open gridpart "]/p//text()'
                        )
                    )
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                self.releases.append(
                    {"text": text.strip(), "title": title.strip(), "url": link.strip()}
                )
            except:
                print("no connection:\n" + link)

    def get(self, save):
        """                                                                             
        Fetches articles from KPN
        """
        try:
            driver = webdriver.PhantomJS()
        except selenium.common.exceptions.WebDriverException:
            logger.critical(
                "Unable to run KPN scraper, no PhantomJS in path. Try (re)installing PhantomJS."
            )
            return []

        driver.get(self.START_URL)
        time.sleep(2)
        # don't ask me why but driver.page_source must explicitly be referenced
        # before continuing
        dummy_page_source = driver.page_source
        tree = fromstring(driver.page_source)

        linkobjects = tree.xpath('//*/article[@class="kpn-clear-fix"]/h3//a')
        links = [l.attrib["href"] for l in linkobjects if "href" in l.attrib]
        # print('\n'.join(links))
        self.process_links(links)

        try:
            button_right = driver.find_element_by_class_name(
                "kpn-icomoon-arrow-right-bold"
            )
            while button_right.get_attribute("class").find("kpn-disabled") == -1:
                button_right.click()
                # processing here
                time.sleep(2)
                linkobjects = tree.xpath('//*/article[@class="kpn-clear-fix"]/h3//a')
                links = [l.attrib["href"] for l in linkobjects if "href" in l.attrib]
                # print('\n'.join(links))
                self.process_links(links)

                button_right = driver.find_element_by_class_name(
                    "kpn-icomoon-arrow-right-bold"
                )
        except:
            print("Error occurred.")

        driver.quit()
        return self.releases
