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

class groenlinks(Scraper):
    """Scrapes Groenlinks"""

    def __init__(self,database=True, maxpages = 2):
        '''
        maxpage: number of pages to scrape
        '''
        
        self.database = database
        self.START_URL = "https://www.groenlinks.nl/nieuws"
        self.BASE_URL = "https://www.groenlinks.nl"
        self.MAXPAGES = maxpages

    def get(self):
        '''                                                                     
        Fetches articles from Groenlinks
        '''
        self.doctype = "Groenlinks (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)


        releases = []

        page = 0
        current_url = self.START_URL+"?page="+str(page)
        overview_page = requests.get(current_url, timeout = 10)
        first_page_text=""
        while overview_page.text!=first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > self.MAXPAGES:
                break
            elif page ==1:
                first_page_text=overview_page.text             
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@class="read-more"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                try:
                    current_page = requests.get(link, timeout = 10)
                except requests.ConnectionError as e:
                    try:
                        link = link[25:]
                        current_page = requests.get(link, timeout = 10)
                    except:
                        logger.debug("Connection Error!")
                        logger.debug(str(e))
                tree = fromstring(current_page.text)
                try:
                    title= " ".join(tree.xpath('//*[@id = "page-title"]/text()'))
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    publication_date = "".join(tree.xpath('//*[@class = "submitted submitted-date"]/text()'))
                    MAAND2INT = {"januari":1, "februari":2, "maart":3, "april":4, "mei":5, "juni":6, "juli":7, "augustus":8, "september":9, "oktober":10, "november":11, "december":12}
                    dag = publication_date[:2]
                    jaar= publication_date[-4:]
                    maand= publication_date[2:-4].strip().lower()
                    publication_date = datetime.datetime(int(jaar), int(MAAND2INT[maand]),int(dag))
                    publication_date = publication_date.date()
                except:
                    publication_date = datetime.datetime(1,1,1)
                try:
                    teaser=" ".join(tree.xpath('//*[@class = "intro"]//p/text()')).strip()
                    teaser = teaser.replace('\n', '')
                    teaser = teaser.replace('\xa0', ' ')
                except:
                    logger.debug("no teaser")
                    teaser = ""
                try:
                    text = " ".join(tree.xpath('//*[@class = "content"]/p/text()')).strip()
                    text = text.replace('\n', '')
                    text = text.replace('\t', '')
                except:
                    logger.info("no text?")
                    text = ""
                try:
                    quote = " ".join(tree.xpath('//*[@class = "content"]//blockquote//p/text()')).strip()
                    quote = quote.replace('\n', '')
                except:
                    quote = ""
                try:
                    whole_release = " ".join(tree.xpath('//*[@id = "page-title"]/text()|//*[@class = "intro"]//p/text()|//*[@class = "content"]/p/text()|//*[@class = "content"]//blockquote//p/text()')).strip()
                    whole_release = whole_release.replace('\n', '')
                    whole_release = whole_release.replace('\t', '')
                    whole_release = whole_release.replace('\xa0', '')
                except:
                    whole_release = ""
                
                #next step necessary as loop somehow runs twice (avoid duplicates)
                dict = ({'text':text,
                                 'teaser': teaser,
                                 'title':title,
                                 'quote':quote,
                                 'url':link,
                                 'publication_date':publication_date,
                         'whole_release':whole_release})
                
                if dict not in releases:
                    releases.append(dict)

            page+=1
            current_url = self.START_URL+'?page='+str(page)
            overview_page=requests.get(current_url, timeout = 10)

        return releases
