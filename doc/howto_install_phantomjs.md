# Install PhantomJS to use for non-RSS scrapers

Some non-rss websites use Javascript to make the lay-out of their websites. In this case, using XPaths when trying to retrieve the articles is not possible from the overview page is not possible. In this case, we will have to use Selenium and PhantomJS to being able to work with the website. An example of such a website is https://overons.kpn/en/news. These websites often do not have a page navigation to loop over. This manual will show you how to install PhantomJS and provide an example of a scrapers using Selenium and PhantomJS.

Go to http://phantomjs.org/download.html and download the version of PhantomJS that is app that is applicable to your operating system. After extracting the zip file copy the file phantomjs to a directory in your path, so python can detect it. You can see the path when you execute the following command in bash:


```python
echo $PATH
```

For instance, I For instance, I put it in the directory ‘/Users/tamara/anaconda/bin’. Put the following command in the head of your python script:


```python
from selenium import webdriver
```

Put the following two commands in the get method:


```python
driver = webdriver.PhantomJS()
driver.get(URL)
```

Below you can see an example of such a scraper containing phantomjs. Now you can test the scraper in INCA as normally. I commented out the download links and packages needed make sure your computer can work with Selenium and PhantomJS in the first 5 lines.


```python
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

class kpn(Scraper):
    """Scrapes KPN"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://corporate.kpn.com/press/press-releases.htm"
        self.BASE_URL = "http://corporate.kpn.com/"
        self.doctype = "KPN"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug('ik ga nu {} ophalen'.format(link))
            try:
                tree = fromstring(requests.get(self.BASE_URL + link).text)
                try:
                    title=" ".join(tree.xpath('//*/h2[@class="article"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*/article[@class="kpn-article kpn-collapsible-open gridpart "]/p//text()'))
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
        Fetches articles from KPN
        '''
        driver = webdriver.PhantomJS()
        driver.get(self.START_URL)
        time.sleep(2)
        # don't ask me why but driver.page_source must explicitly be referenced
        # before continuing
        dummy_page_source = driver.page_source
        tree = fromstring(driver.page_source)

        linkobjects = tree.xpath('//*/article[@class="kpn-clear-fix"]/h3//a')
        links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
        # print('\n'.join(links))
        self.process_links(links)
    
        try:
            button_right = driver.find_element_by_class_name("kpn-icomoon-arrow-right-bold")
            while button_right.get_attribute("class").find("kpn-disabled") == -1:
                button_right.click()
                # processing here
                time.sleep(2)
                linkobjects = tree.xpath('//*/article[@class="kpn-clear-fix"]/h3//a')
                links = [l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
                # print('\n'.join(links))
                self.process_links(links)

                button_right = driver.find_element_by_class_name("kpn-icomoon-arrow-right-bold")
        except:
            print('Error occurred.')

        driver.quit()
        return self.releases

```
