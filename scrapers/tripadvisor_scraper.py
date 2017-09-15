import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange

logger = logging.getLogger(__name__)

# give more output
logger.setLevel(logging.DEBUG)

# for testing purposes, never fetch more than this many pages of reviews
# set to 1000 or so for production use
MAXPAGES = 2


class tripadvisor(Scraper):
    """Scrapes Tripadvisor reviews"""
    
    def __init__(self,database=True,maxpages = 2, maxreviewpages = 5, starturl = "https://www.tripadvisor.com/Hotels-g188590-Amsterdam_North_Holland_Province-Hotels.html"):
        '''
        maxpage: number of pages with hostels to scrape
        maxreviewpages: number of pages with reviews *per hostel* to scrape
        starturl: URL to first page with hostel results
        '''
        self.database=database
        self.START_URL = starturl
        self.BASE_URL = "http://www.tripadvisor.com"           # MET OF ZONDER /?
        self.MAXPAGES = maxpages
        self.MAXREVIEWPAGES = maxreviewpages

        
    def get(self):
        '''Fetches reviews from Tripadvisor.com'''
        self.doctype = "Tripadvisor reviews"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=8)
        
        hotels = []

        allurls = []
        starturl = "https://www.tripadvisor.com/Hotels-g188590-0a{}-Amsterdam_North_Holland_Province-Hotels.html#BODYCON"
        for i in range (0, 30, 30):          # AANPASSEN!!
            allurls.append(starturl.format(i))
        allurlsgen = (e for e in allurls)
        thisurl = next(allurlsgen)
        sleep(randrange(5,10))
        overview_page = requests.get(thisurl)
        logger.debug("Fetched {}".format(thisurl))
        # the while loop ensures that we stop once we get an empty page
        while overview_page.text.find('prw_rup prw_meta_hsx_three_col_listing')!=-1:
            tree = fromstring(overview_page.text)
            linkselement =tree.xpath('//*[@class="property_title"]')
            links = [e.attrib['href'] for e in linkselement if 'href' in e.attrib]
            names =tree.xpath('//*[@class="property_title"]/text()')

            assert len(links)==len(names)

            for i in range(len(links)):
                thishotel = {'name':names[i].strip(),
                             'link':links[i].strip()}
                hotels.append(thishotel)
            # apart from the initial while-loop condition, we also
            # stop the loop once we reach the maximum number of
            # pages defined before:
            try:
                next_url = next(allurlsgen)
            except StopIteration:
                break
            sleep(randrange(5,10))
            overview_page = requests.get(next_url)
            logger.debug("Fetched {}".format(next_url))
            
        logger.debug('We hebben net alle overzichtspagina\'s opgehaald. Er zijn {} hotels'.format(len(hotels)))
        # Fetch hotel-specific webpages and enrich the hotel dicts
        hotels_enriched = []
        for hotel in hotels:
            logger.debug(hotel)
            link = self.BASE_URL + hotel['link']
            logger.debug('ik ga nu {} ophalen'.format(link))
            sleep(randrange(5,10))
            current_page = requests.get(link)
            tree = fromstring(current_page.text)

            # BUILD IN A STOP !!!
            # If the same link is requested again, break
            
            try:
                overallrating = tree.xpath('//*[@class="overallRating"]/text()')[0]
            except:
                ""
                logger.info("Hotel with link {} did not have an overall rating.".format(link))
                continue
            thishotel = hotel
            try:
                thishotel['overall_rating'] = float(overallrating.strip())
            except:
                thishotel['overall_rating'] = overallrating.strip()
                
            # Fetch hotel-specific reviews and enrich the hotel dicts
            
            reviews_thishotel=[]

            # we check how many pages with reviews there are
            maxpages = int(tree.xpath('//*[@class="pageNum last taLnk "]/text()')[0])
            # but if these are more than our maximum set above, we only take so much
            if maxpages > MAXPAGES:
                logger.debug('There seem to be {} pages with reviews, however, we are only going to scrape {}'.format(maxpages,MAXPAGES))
                maxpages = MAXPAGES
            
            reviews_baseurl = self.BASE_URL + hotel['link']       # is dit de juist link?
            splitat = reviews_baseurl.find("Reviews-")+8

            for ppp in range(maxpages):
                pagenumber = ppp*5         # in the link the pagenumber is times 5
                reviews_thisurl = reviews_baseurl[:splitat]+"or{}-".format(pagenumber)+reviews_baseurl[splitat:]
            
                sleep(randrange(5,10))
                current_page = requests.get(reviews_thisurl)
                logger.debug("Ik ga nu de reviews van {} ophalen".format(reviews_thisurl))
                tree = fromstring(current_page.text)
                review_relativedate = tree.xpath('//*[@class="ratingDate relativeDate"]/text()')     
                review_username = tree.xpath('//*[@class="username mo"]//text()')
            
                assert len(review_relativedate)==len(review_username)

                for i in range(len(review_username)):
                    reviews_thishotel.append({'username':review_username[i].strip(),
                                          'reviewdate':review_relativedate[i].strip()})
                thishotel['reviews'] = reviews_thishotel

            hotels_enriched.append(thishotel)

        logger.debug('We hebben net alle overzichtspagina\'s opgehaald. Er zijn {} hotels'.format(len(review_username)))
        return hotels_enriched


def cleandoc(document):
    for k,v in document.items():
        if type(v)==dict:
            document[k] = cleandoc(v)
        elif type(v)==str:
            if not v.replace('\n','').replace(' ',''):
                document[k] = ""
            else:
                document[k] = v
        elif type(v) == str:
            pass

    empty_keys = []
    for k in document.keys():
        if not k.replace('\n','').replace(' ','') and not document[k]:
            empty_keys.append(k)
    for k in empty_keys:
        document.pop(k)
    return document




