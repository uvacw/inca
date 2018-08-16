# When testing or actual scraping, specify desired year to be processed as a parameter to the class:
# from inca import Inca; myinca = Inca(); data = myinca.scrapers.irishparliament(save=False, year=2018)
# scrape per question instead per page

import requests
import datetime
from calendar import monthrange
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

MAAND2INT = {'January':1,'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}

class irishparliament(Scraper):
    """Scrapes Irish parliament"""

    def __init__(self):
        self.BASE_URL = "https://www.oireachtas.ie"
        self.doctype = "irishparliament (par)"
        self.version = ".1"
        self.date = datetime.datetime(year=2018, month=7, day=3)

    def get(self, save, year):
        '''                                                                             
        Fetches questions from Irish parliament
        '''

        releases = []

        for month in range(1, 13):
            fromDate = datetime.datetime(year, month, 1)
            toDate = datetime.datetime(year, month, monthrange(year, month)[1])
  
            fromDateStr = str(fromDate.day) + '/' + str(fromDate.month) + '/' + str(fromDate.year)
            toDateStr = str(toDate.day) + '/' + str(toDate.month) + '/' + str(toDate.year)
            print(fromDateStr, toDateStr)

            try:
                page_num = 1
                
                while True:
                    
                    page = requests.get('https://www.oireachtas.ie/en/debates/questions/?page=' + str(page_num) + '&datePeriod=dates&toDate=' + toDateStr + '&fromDate=' + fromDateStr + '&questionType=all')
                    
                    if page.text.find('Sorry no matches were found for this query.') != -1:
                        print(str(page_num) + ' niet gevonden')
                        break

                    print(page_num)
                    page_num += 1

                    tree = fromstring(page.text)
                    linkobjects = tree.xpath('//*[@id="content-start"]/div[3]/div[2]/div/div/div/div[4]/a')
                    links = [self.BASE_URL + l.attrib['href'] for l in linkobjects]
                    print(links)

                    for link in links: 
                        logger.debug('ik ga nu {} ophalen'.format(link))
                        current_page = requests.get(link)
                        tree = fromstring(current_page.text)
                        try:
                            title=tree.xpath('//*[@class="c-hero__content"]/h1[@class="c-hero__title"]//text()')
                            print(title)
                        except:
                            print("no title")
                            title = []
                        try:
                            d = tree.xpath('//*/h2[@class="u-text-h2 -underline c-parliamentary-question__heading"]//text()')[0].strip()
                            d2 = re.findall(r'(?<= , ).*',d)[0]
                            print(d2)
                       #    jaar = int(d[-4:])
                       #    maand = MAAND2INT(d[-7:-5])
                       #    dag = int(d[-10:-8])
                       #    datum = datetime.datetime(jaar,maand,dag)
                       #    print(datum)
                        except Exception as e:
                            print('could not parse date')
                            print(e)
                            datum = None          
                        try:
                            questioners=tree.xpath('//*/a[@class="c-avatar__name-link"]//text()')
                            print(questioners)
                        except Exception as e:    
                            questioners= []
                        #try:
                        #    text = "".join(tree.xpath('//*/div[@class="content")/p//text'))
                        #except:
                        #    logger.info("oops - geen textrest?")
                        #    text = ""
                        
                        # We now collected lists of questioners, datums, and so on. They should have equal length
                        print(title)
                        print(questioners)

                        assert len(title) == len(questioners)  == len(url)

                        for i in range(len(title)):
                            yield {'title': title[i].strip(),
                                'questioners':questioners[i].strip}

                        #releases.append({'title':title.strip(),
                        #                 'text':text.strip(),
                        #                 'questioners':questioners.strip(),
                        #                 'date':datum,
                        #                 'url':link.strip()})
        
            except Exception as e:
                print(e)

        return releases