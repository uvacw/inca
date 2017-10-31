import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange
import urllib.request as urllib2

logger = logging.getLogger(__name__)

# gives more output
logger.setLevel(logging.DEBUG)

# For testing purposes, never fetch more than this many pages of reviews
# set to 1000 or so for production use
# MAXPAGES = 2

class tripadvisor(Scraper):
    """Scrapes Tripadvisor reviews"""
    
    def __init__(self, database=True, maxpages = 2, maxreviewpages = 5, maxurls = 50, starturl = "https://www.tripadvisor.com/Hotels-g188590-Amsterdam_North_Holland_Province-Hotels.html"):
        '''
        maxpages: number of pages with hostels to scrape
        maxreviewpages: number of pages with reviews *per hostel* to scrape
        starturl: URL to first page with hostel results
        maxurl: number of urls that are made
        '''
        self.database = database
        self.START_URL = starturl
        self.BASE_URL = "http://www.tripadvisor.com"          
        self.MAXPAGES = maxpages
        self.MAXREVIEWPAGES = maxreviewpages
        self.MAXURLS = maxurls
        self.BLACKLIST = ["http://www.tripadvisor.com/Hotel_Review-g188590-d189389-Reviews-Sofitel_Legend_The_Grand_Amsterdam-Amsterdam_North_Holland_Province.html","http://www.tripadvisor.com/Hotel_Review-g188590-d3526884-Reviews-Andaz_Amsterdam_Prinsengracht-Amsterdam_North_Holland_Province.html"]   # review pages that never should be fetched (e.g., because they do not conform with the standard layout)
 
    def get(self):
        '''Fetches reviews from Tripadvisor.com'''
        self.doctype = "Tripadvisor reviews"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=8)
        
        hotels = []
        allurls = []

        # Creating the starturl by altering the starturl
        starturl_altering = self.START_URL + "#BODYCON"
        occur = 2
        indices = [x.start() for x in re.finditer("-",starturl_altering)]
        part1 = starturl_altering[0:indices[occur-1]]
        part2 = starturl_altering[indices[occur-1]+1:]
        starturl = part1 + "-oa{}-" + part2

        # Possible urls are created, but the list can't be longer than the maxpages defined above
        for i in range (0, self.MAXURLS*30, 30):          
            allurls.append(starturl.format(i))
        if len(allurls) > self.MAXPAGES:
            allurlsgen = (e for e in allurls[:int(self.MAXPAGES)])
            logger.debug('The list of created URLs is longer than the defined max overviewpages. {} page(s) are being scraped'.format(self.MAXPAGES))
        else:
            allurlsgen = (e for e in allurls)
            logger.debug('The list of created URLs is shorter than the defined max overviewpages. {} page(s) are being scraped'.format(len(allurls)))
        thisurl = next(allurlsgen)
        sleep(randrange(5,10))
        req=urllib2.Request(thisurl, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
        htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
        logger.debug("Fetched the overviewpage: {}".format(thisurl))
        while htmlsource.find('prw_rup prw_meta_hsx_three_col_listing')!=-1:
            tree = fromstring(htmlsource)
            linkselement = tree.xpath('//*[@class="property_title"]')
            links = ["http://www.tripadvisor.com"+ e.attrib['href'] for e in linkselement if 'href' in e.attrib]
            names = tree.xpath('//*[@class="property_title"]/text()')
            reviewsquantity = tree.xpath('//*[@class="more review_count"]//text()')

            assert len(links)==len(names)==len(reviewsquantity)

            for i in range(len(links)):
                thishotel = {'name':names[i].strip(),
                             'link':links[i].strip(),
                             'reviewquantity':reviewsquantity[i].strip()}
                hotels.append(thishotel)
            # apart from the initial while-loop condition, we also stop the loop once we reach
            # the maximum number of pages defined before:
            try:
                next_url = next(allurlsgen)
            except StopIteration:
                break
            sleep(randrange(5,10))
            req=urllib2.Request(next_url, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
            htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
            logger.debug("Fetched the overviewpage: {}".format(next_url))
            
        logger.debug('We have fetched all overviewpages that exist (or the max number of pages defined). There are {} hotels in total.'.format(len(hotels)))
        # Fetch hotel-specific webpages and enrich the hotel dicts
        hotels_enriched = []
        for hotel in hotels:
            logger.debug(hotel)
            link = hotel['link']
            logger.debug('Fetched the hotel-specific webpage: {}'.format(link))
            sleep(randrange(5,10))

            if link not in self.BLACKLIST:
                req=urllib2.Request(link, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
                htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(htmlsource)
                try:
                    overallrating = tree.xpath('//*[@class="overallRating"]/text()')[0]
                    logger.debug("This page has an overall rating of {}.".format(overallrating))
                except:
                    ""
                    logger.info("Hotel with link {} did not have an overall rating.".format(link))
                try:
                    ranking = "".join(tree.xpath('//*[@class="header_popularity popIndexValidation"]/a/text() | //*[@class="header_popularity popIndexValidation"]/b/text() | //*[@class="header_popularity popIndexValidation"]/text()'))
                    logger.debug("This page has a ranking of {}.".format(ranking))
                except:
                    ""
                    logger.info("Hotel with link {} did not have a ranking.".format(link))   
                    
                thishotel = hotel
                thishotel['ranking'] = ranking.strip()
                try:
                    thishotel['overall_rating'] = float(overallrating.strip())
                except:
                    thishotel['overall_rating'] = overallrating.strip()
            else:
                logger.debug('This link was not fetched since it is in the blacklist: {}'.format(link))
                continue
                
            # Fetch hotel-specific reviews and enrich the hotel dicts
            reviews_thishotel=[]

            # the hotel-specific webpage shows the reviews, but only with limited text
            # so we go to the link of the first review which will give an extended list of all reviews

            linkelement_reviewpage = tree.xpath('//*[@class="quote isNew"]/a | //*[@class="quote"]/a')
            link_reviewpage = [e.attrib['href'] for e in linkelement_reviewpage if 'href' in e.attrib][0]
            reviews_thisurl = self.BASE_URL + link_reviewpage

            # we check how many pages with reviews there are, for this we only need the first review page of the hotel
            req=urllib2.Request(reviews_thisurl, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
            htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
            tree = fromstring(htmlsource)
            maxpages = int(tree.xpath('//*[@class="pageNum last taLnk "]/text()')[0])
            logger.debug('There seem to be {} pages with reviews.'.format(maxpages))
            
            # but if these are more than our maximum set above, we only take so much
            if maxpages > self.MAXREVIEWPAGES:
                logger.debug('There seem to be {} pages with reviews, however, we are only going to scrape {}.'.format(maxpages,self.MAXREVIEWPAGES))
                maxpages = self.MAXREVIEWPAGES

            i = 1
            while True:
                sleep(randrange(5,10))
                req=urllib2.Request(reviews_thisurl, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
                htmlsource=urllib2.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                logger.debug("Fetched the reviews of hotel-specific webpage: {}.".format(reviews_thisurl))
                tree = fromstring(htmlsource)
                try:
                    date_element = tree.xpath('//*[@class="ratingDate relativeDate"]')
                    review_date = [e.attrib['title'] for e in date_element if 'title' in e.attrib]
                    logger.debug("This page has {} dates.".format(len(review_date))) 
                except:
                    ""
                    logger.info("Hotel with link {} did not have a date.".format(reviews_thisurl))
                try:
                    review_headline = tree.xpath('//*[@class="noQuotes"]//text()')
                    logger.debug("This page has {} headlines.".format(len(review_headline))) 
                except:
                    ""
                    logger.info("Hotel with link {} did not have a headline.".format(link))
                try:
                    mobiles = tree.xpath('//*[@class="rating reviewItemInline"]')
                    review_mobile = [True if i.xpath('./a') else False for i in mobiles]
                    logger.debug("This page has {} type of reviews.".format(len(review_mobile)))
                except:
                    ""
                    logger.info("Hotel with link {} did not have a type of review.".format(link))
                try:
                    ratingelements = tree.xpath('//*[@class="rating reviewItemInline"]/span[1]')
                    review_ratings = [e.attrib['class'].lstrip('ui_bubble_rating bubble_') for e in ratingelements]
                    logger.debug("This page has {} ratings.".format(len(review_ratings)))
                except:
                    ""
                    logger.info("Hotel with link {} did not have a review ratings.".format(reviews_thisurl))

                review_stayed = []
                review_stayed_elem = tree.xpath('//*[@class="prw_rup prw_reviews_category_ratings_hsx"]')
                for review in review_stayed_elem:
                    date = review.text_content()
                    date_strip = date.replace("Value","").replace("Location","").replace("Sleep","").replace("Quality","").replace("Rooms","").replace("Cleanliness","").replace("Service","")
                    if date_strip == "":
                        review_stayed.append('NA')
                    else:
                        review_stayed.append(date_strip)
                logger.debug("This page has {} dates of stay.".format(len(review_stayed)))
                
                review_usernames =[]
                review_locations=[]
                review_contributions=[]
                review_votes=[]
                bios = tree.xpath('//*[@class="member_info"]')
                review_usernames =[]
                review_locations=[]
                review_contributions=[]
                review_votes=[]
                bios = tree.xpath('//*[@class="member_info"]')
                for b in bios:
                    allinfo = b.getchildren()
                    if b.getchildren()[0].text_content() == '':
                        review_usernames.append(b.getchildren()[1].text_content())
                        review_locations.append('NA')
                    else:                    
                        relevantinfo = allinfo[0].getchildren()
                        review_usernames.append(relevantinfo[1].text_content())
                        if len(relevantinfo) == 3:
                            review_locations.append(relevantinfo[2].text_content())
                        else:
                            review_locations.append('NA')
                    userinfo = allinfo[0].getchildren()
                    userhistory_elements = allinfo[1].getchildren()
                    userhistory = userhistory_elements[0].getchildren()     
                    if len(userhistory) == 4:
                        review_contributions.append(userhistory[1].text_content())
                        review_votes.append(userhistory[3].text_content())
                    elif len(userhistory) == 2:
                        review_contributions.append(userhistory[1].text_content())      
                        review_votes.append('NA')
                    else:
                        review_contributions.append('NA')
                        review_votes.append('NA')
                logger.debug("This page has {} user contributions.".format(len(review_contributions)))
                logger.debug("This page has {} user votes.".format(len(review_votes)))
                logger.debug("This page has {} user locations.".format(len(review_locations)))
                logger.debug("This page has {} usernames.".format(len(review_usernames)))

                review_images = []
                reviews = tree.xpath('//*[@class="innerBubble"]/div[@class="wrap"]')

                for r in reviews:
                    if r.find('*//noscript/img') is not None:  
                        review_images.append([{'url':e.attrib['src']} for e in r.findall('*//noscript/img')])
                    else:
                        review_images.append([])
                
                review_moreratings = []
                for r in reviews:
                    allratings = {}
                    review_ratingthing = []
                    review_ratingvalue = []
                    review_allratings = r.findall('*//li')[1:]
                    for rating in review_allratings:
                        review_ratingthing.append(rating.text_content())
                        review_ratingvalue.append(rating[0].items()[0][1][-2:])
                        assert len(review_ratingthing)==len(review_ratingvalue)
                        allratings = dict(zip(review_ratingthing,review_ratingvalue))
                    review_moreratings.append(allratings)

                review_is_sponsored = []
                for review in reviews:
                    is_sponsored = review.text_content().find('Review collected in partnership with') > -1
                    review_is_sponsored.append(is_sponsored)
             
                # go to the next page, unless there is no next page   
                next_reviewpageelement = tree.xpath('//*[@class="nav next taLnk "]')
                if next_reviewpageelement == []:
                    break
                else:
                    next_pagelink = [e.attrib['href'] for e in next_reviewpageelement if 'href' in e.attrib][0]
                    reviews_thisurl = self.BASE_URL + next_pagelink
                i+=1
                if i > maxpages:
                    break

                assert len(review_usernames)==len(review_date)==len(review_headline)==len(review_mobile)==len(review_stayed)==len(review_ratings)==len(review_locations)==len(review_votes)==len(review_contributions)
                
                logger.debug('The length of images is {}'.format(len(review_images)))
                logger.debug('The length of moreratings is {}'.format(len(review_moreratings)))
                logger.debug('The length of review_is_sponsored is {}'.format(len(review_is_sponsored)))     

                # Now scraping the text of the reviews, including the responses. First, all text (reviews and responses)
                # is gathered. Responses are then matched to the right review based on the order of the text
                # (responses always follow the review).
                
                reviews_cleaned = []
                reviews_alltext_elements = tree.xpath('//*[@class="partial_entry"]')
                reviews_alltext = [e.text_content() for e in reviews_alltext_elements]

                # check if we have any review that has no text:
                notcomplete = max([r=="" for r in reviews_alltext])  # True if at least one review is empty
                if notcomplete:
                    logger.warning("This is weird, the current hotel has a review without text. It's here: {}".format(reviews_thisurl))
                    continue
                responses_elements = tree.xpath('//*[@class="mgrRspnInline"]')
                responses = [e.text_content() for e in responses_elements]
                responses_date = []
                responses_responder = []
                responses_text = []
                for r in responses:
                    splitat = r.find('Responded')
                    responder, text = r[:splitat], r[splitat:]
                    responses_responder.append(responder)
                    splitat_date = text.find('ago')+3
                    date, review = text[:splitat_date], text[splitat_date:]
                    responses_date.append(date)
                    splitat_text = review.find('Report response')
                    review_strip = review[:splitat_text]
                    responses_text.append(review_strip)
                for line in reviews_alltext:
                    if line not in responses_text:
                        reviews_cleaned.append({'review':line})         
                    else:
                        reviews_cleaned[-1]['response']=line
                #logger.debug('The length of response dates is {}'.format(len(responses_date)))
                #logger.debug('The length of responders is {}'.format(len(responses_responder)))
                #logger.debug('The length of responses is {}'.format(len(responses_text)))
                assert len(responses_date)==len(responses_responder)==len(responses_text)
                
                # Add keys to the dicts
                responses_date_iter = iter(responses_date)
                responses_responder_iter = iter(responses_responder)
                for review in reviews_cleaned:
                    if 'response' in review:
                        review['date'] = next(responses_date_iter)
                        review['responder'] = next(responses_responder_iter)

                logger.debug("This page has {} reviews.".format(len(review_usernames)))
                
                for i in range(len(review_usernames)):
                    reviews_thishotel.append({'username':review_usernames[i].strip(),
                                              'date':review_date[i].strip(),
                                              'headline':review_headline[i].strip(),
                                              'mobile':review_mobile[i],
                                              'date_stay':review_stayed[i],
                                              'rating':review_ratings[i],
                                              'location':review_locations[i],
                                              'votes':review_votes[i],
                                              'contributions':review_contributions[i],
                                              'review':reviews_cleaned[i],
                                              'images':review_images[i],
                                              'specific_ratings':review_moreratings[i],
                                              'partnership':review_is_sponsored[i]
                                              })
                thishotel['reviews'] = reviews_thishotel

            hotels_enriched.append(thishotel)

        logger.debug('We have fetched all reviews from the hotel-specific webpage that exist. There are {} reviews in total'.format(len(review_usernames)))
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

