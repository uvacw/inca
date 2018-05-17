from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from time import sleep
import logging
import math
import datetime
import re
from core.scraper_class import Scraper

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class expedia(Scraper):
    """Scrapes Expedia reviews"""
    
    def __init__(self, database=True, startpage = 1, maxpages = 1, maxreviewpages = 5, cityname = "Amsterdam"):
        '''
        database: whether to save the results in the database (default = True)
        startpage: the overview page where to start scraping
        maxpages: number of overview pages with hotels to scrape at one time
        maxreviewpages: number of pages with reviews per hotel to scrape
        cityname: name of the city which to search for
        '''
        self.database       = database         
        self.MAXPAGES       = maxpages
        self.STARTPAGE      = startpage
        self.MAXREVIEWPAGES = maxreviewpages
        self.CITYNAME       = cityname

    def get(self):
        '''Fetches reviews from Expedia.com'''
        self.doctype = "expedia_hotel"
        self.version = ".1"
        self.date    = datetime.datetime(year=2018, month=4, day=25)

        # Store information for testing
        file = open('noreviews.txt','w')

        driver = webdriver.Firefox(executable_path=r'/home/lisa/INCA/inca/geckodriver')
        driver.get("https://www.expedia.com")
        
        hotelsonly = driver.find_element_by_id("tab-hotel-tab-hp") 
        hotelsonly.click()
        sleep(2)
        destination = driver.find_element_by_id("hotel-destination-hp-hotel")
        destination.send_keys(self.CITYNAME) 
        destination.send_keys(Keys.RETURN)
        logger.debug('Scraping the hotels in {}.'.format(self.CITYNAME))
        sleep(10)

        # Check how many hotels there are to find the last overview page:
        page_indicator = driver.find_elements_by_class_name("showing-results")[0].text
        amount_hotels_total = [int(s) for s in page_indicator.split() if s.isdigit()][-1]
        last_page = math.ceil(amount_hotels_total/50)
        logger.debug('The last page is {}.'.format(last_page))
        if self.MAXPAGES >= last_page:
            logger.debug('Scraping {} pages of hotels'.format(last_page))
        else:
            logger.debug('Scraping {} pages of hotels'.format(self.MAXPAGES))
        # Write the amount of pages to a file, which can be read by the scraper helper:
        with open('maxpages_expedia.txt',mode='w') as f:
            f.write(str(last_page))
            
        # Get all the elements from each overview page:
        # check whether the 'next page' button is available in a while loop
        number_overviewpage = 1
        onlastpage = 0
        window_overviewpage = driver.window_handles[0]
        while onlastpage == 0:
            # Locate the page that we're going to scrape:
            if number_overviewpage < self.STARTPAGE:
                logger.debug("This is the page we want to scrape: {}, however, we're on page {}".format(self.STARTPAGE,number_overviewpage))
                try:
                    results_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "resultsContainer")))
                    logger.debug('Results section found')
                    next_page = driver.find_element_by_class_name('pagination-next')
                    next_page.click()
                    logger.debug('Going to the next page')
                    sleep(3)
                    number_overviewpage += 1
                    continue
                except TimeoutException as ex:
                    logger.error('ERROR: results section not found for overview page {}, with '.format(number_overviewpage))
                    logger.error('Exception:'+str(ex))
            else:
                logger.debug('This is the page we want to scrape.')
            # Check whether this page is the last page:
            if number_overviewpage == last_page:
                logger.debug('On the last overview page ({})'.format(number_overviewpage))
                onlastpage = 1
            elif number_overviewpage == self.MAXPAGES:
                logger.debug('On the maximum defined overview page ({})'.format(number_overviewpage))
                onlastpage = 1
            else:
                logger.debug('On overview page {}/{}'.format(number_overviewpage,last_page))
            try:
                results_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "resultsContainer")))
                logger.debug('Results section found')
                sleep(10)
                # Find all article elements:
                hotels = driver.find_elements_by_css_selector('section article')
                # Find all sponsored article elements:
                sponsored_hotels = driver.find_elements_by_css_selector('section [id$=sponsored]')
                logger.debug('There are {} hotels on this overviewpage, of which {} are sponsored hotels.'.format(len(hotels),len(sponsored_hotels)))
                # Length of articles should be 50 (without sponsored articles)
                if len(hotels)-len(sponsored_hotels) > 50:
                    logger.debug('List of hotels is longer than 50, there are probably {} banner(s) or decoy(s) in the list.'.format(len(hotels)-len(sponsored_hotels)-50))
                    n = 0
                    banner = -1
                    for hotel in hotels:
                        if hotel.get_attribute("id") == 'MODBanner':
                            logger.debug('Found a banner, it is the {}th item'.format(n))
                            banner = n
                        n += 1
                    if banner == -1:
                        logger.debug('OOPS, no banner was found! The length is still {}'.format(len(hotels)))
                    # remove these elements from the list!!!
                    del hotels[(banner)]
                    if len(hotels)-len(sponsored_hotels) == 50:
                        logger.debug('The final list of hotels now contains 50 hotels, without sponsored hotels')
                    else:
                        logger.error('OOPS, the final list of hotels contains {} hotels'.format(len(hotels)-len(sponsored_hotels)))
                elif (len(hotels)-len(sponsored_hotels) < 50 and onlastpage == 0):
                    logger.error('OOPs, there are less than 50 hotels found, while this is not the last page!')
                # Go to each hotel on this overview page:
                number_hotelpage = 1
                for hotel in hotels:
                    url_button = hotel.find_element_by_css_selector('.flex-link')
                    url = hotel.find_element_by_css_selector('.flex-link').get_attribute('href')
                    # See if there is an external link (changes how to deal with the hotel):
                    external_url = hotel.find_element_by_css_selector('.flex-link').get_attribute('data-externalurl')
                    if (external_url != None and external_url != ''):
                        logger.debug("This hotel has an external link, so we're skipping hotel page {}/{}".format(number_hotelpage,len(hotels)))
                        number_hotelpage += 1
                        continue
                    else:
                        url = url
                    # Go to the hotel page
                    url_button.click()
                    sleep(5)
                    window_hotelpage = driver.window_handles[1]
                    driver.switch_to_window(window_hotelpage)
                    logger.debug('On hotel page {}/{} of overview page {}/{}'.format(number_hotelpage,len(hotels),number_overviewpage,last_page))
                    try:
                        hotel_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "price-compare-list")))
                        logger.debug('Hotel information section found')

                        # Find all the information needed from the hotel page
                        try:
                            name = driver.find_element_by_css_selector('#hotel-name').text
                        except NoSuchElementException as ex:
                            logger.debug('No hotel name was found')
                            name = None
                        try:
                            stars = driver.find_element_by_css_selector('.star-rating-wrapper').text
                        except NoSuchElementException as ex:
                            logger.debug('No hotel quality star were found')
                            stars = None
                        try:
                            rating = float(driver.find_element_by_css_selector('.rating-scale').text.split(' ')[0])
                        except NoSuchElementException as ex:
                            rating = None
                        if rating is None:
                            try:
                                rating = float(driver.find_element_by_css_selector('.rating-scale-bold').text.split(' ')[0])
                            except NoSuchElementException as ex:
                                logger.error('No rating was found')
                                rating = None
                        try:
                            review_quantity = int(driver.find_element_by_css_selector('#link-to-reviews > span').text.replace(',',''))
                        except NoSuchElementException as ex:
                            logger.error('No review quantity was found')
                            review_quantity = None
                        
                        # Add all information to a dict:
                        thishotel = {'url':url.strip(),
                                     'id':number_hotelpage-1,
                                     'name':name.strip(),
                                     'stars':stars.strip(),
                                     'rating':rating,
                                     'review_quantity':review_quantity,
                                     'reviews':[]}
                        logger.debug(thishotel.keys())
                        logger.debug('Retrieved all information from the hotel page')
                        sleep(3)

                        # Go to the review element
                        try:
                            link = driver.find_element_by_css_selector('#link-to-reviews')
                            logger.debug('Found a link to the reviews')
                            sleep(5)
                            link.click()
                            try:
                                results_section = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CLASS_NAME, "review-summary")))
                                logger.debug('Review section found')
                                # Check how many hotels there are to find the last overview page:
                                page_indicator_review = driver.find_element_by_class_name("showing-results").text
                                amount_reviews_total = [int(s) for s in page_indicator_review.split() if s.isdigit()][-1]
                                last_page_review = math.ceil(amount_reviews_total/10)
                                if self.MAXREVIEWPAGES >= last_page_review:
                                    logger.debug('Scraping {} pages of reviews'.format(last_page_review))
                                else:
                                    logger.debug('Scraping {}/{} pages of reviews'.format(self.MAXREVIEWPAGES,last_page_review))
                                
                                # Get all the elements from each review page:
                                allreviews = []
                                number_reviewpage = 1
                                onlastpage_review = 0
                                while onlastpage_review == 0:
                                    # Check whether this page is the last page:
                                    if number_reviewpage == last_page_review:
                                        logger.debug('On the last review page {}/{}'.format(number_reviewpage,last_page_review))
                                        onlastpage_review = 1
                                    elif number_reviewpage >= self.MAXREVIEWPAGES:
                                        logger.debug('On the maximum defined overview page {}/{}'.format(number_reviewpage,self.MAXREVIEWPAGES))
                                        onlastpage_review = 1
                                    else:
                                        logger.debug('On review page {}/{}'.format(number_reviewpage,last_page_review))
                                    try:
                                        results_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "reviews")))
                                        logger.debug('Review section was found for page {}.'.format(number_reviewpage))

                                        # Gather information from the reviews
                                        try:
                                            subratings_elements = driver.find_elements_by_css_selector('.dimensions > div')
                                        except NoSuchElementException as ex:
                                            logger.error('No subratings were found')
                                            subratings_elements = None
                                        if subratings_elements is not None:
                                            subratings = {}
                                            for sub in subratings_elements:
                                                rating, category = sub.text.split(" ",1)
                                                subratings[category] =  rating
                                            thishotel['subratings'] = subratings
                                        try: 
                                            reviews = driver.find_elements_by_css_selector('#reviews > article')
                                            if len(reviews) < 10:
                                                if number_reviewpage == last_page_review:
                                                    logger.debug("Less than 10 reviews were found, however, we're on the last page")
                                                else:
                                                    logger.error("Less than 10 reviews were found, but we're not on the last page")
                                            elif len(reviews) == 10:
                                                logger.debug('All reviews were found')
                                            # Get information from the English reviews
                                            
                                            for review in reviews:
                                                try:
                                                    review.find_element_by_css_selector('.translate-container')
                                                except:
                                                    try:
                                                        title = review.find_element_by_css_selector('.review-title').text
                                                    except:
                                                        title = None
                                                    try:
                                                        date = review.find_element_by_css_selector('.date-posted').text
                                                    except:
                                                        date = None
                                                    try:
                                                        userinformation = review.find_element_by_css_selector('.user-information')
                                                    except:
                                                        userinformation = None
                                                    try:
                                                        username = userinformation.find_elements_by_css_selector('div')[0].text
                                                    except:
                                                        username = None
                                                    try:
                                                        country = userinformation.find_elements_by_css_selector('div')[1].text
                                                    except:
                                                        country = None
                                                    try:
                                                        rating = float(review.find_element_by_css_selector('.rating-header-container span').text)
                                                    except:
                                                        rating = None
                                                    try:
                                                        review_elem = review.find_element_by_css_selector('.review-text')
                                                        if review_elem.find_element_by_css_selector('div').text == 'Read More':
                                                            review_elem.find_element_by_css_selector('.toggle-text').click()
                                                            review_text = review.find_element_by_css_selector('.review-text').text.replace("\nRead Less",'')
                                                        else:
                                                            review_text = review_elem.text
                                                    except:
                                                        review_text = None
                                                    try:
                                                        upvotes = int(review.find_element_by_css_selector('.thanks-count').text)
                                                    except:
                                                        upvotes = None

                                                    thisreview = {'title':title,
                                                                  'date':date,
                                                                  'username':username,
                                                                  'country':country,
                                                                  'rating':rating,
                                                                  'review':review_text,
                                                                  'upvotes':upvotes}
                                                    allreviews.append(thisreview)
                                            thishotel['reviews'] += allreviews

                                        except NoSuchElementException as ex:
                                            logger.error('No reviews were found')
                                            reviews = None
                                            
                                        logger.debug('Retrieved all information from this review page')                                        
                                        # going to the next page, however, not when on the last page
                                        if number_reviewpage == last_page_review:
                                            logger.debug('This was the last review page, breaking now.')
                                            #break
                                        elif number_reviewpage >= self.MAXREVIEWPAGES:
                                            logger.debug('We have reached the maximum defined review pages, breaking now.')
                                            #break
                                        else:
                                            next_page_review = driver.find_element_by_class_name('pagination-next')
                                            next_page_review.click()
                                            logger.debug('Going to the next review page')
                                            sleep(3)
                                        number_reviewpage += 1

                                    except TimeoutException as ex:
                                        logger.error('Review section not found on this page {}.'.format(number_reviewpage))
                                
                            except TimeoutException as ex:
                                logger.error('Review section not found for this hotel {}.'.format(number_hotelpage))
                                file = open("noreviews.txt","a")
                                file.write(thishotel['url']+'\n')
                                file.close()
                            
                        except NoSuchElementException as ex:
                            logger.error('No link to the reviews was found')

                        yield thishotel
                        
                    except TimeoutException as ex:
                        logger.debug('ERROR: hotel information section not found for this hotel {} with error:{}'.format(number_hotelpage,str(ex)))
                    
                    # Close the window and focus back on the overview page
                    driver.close()
                    driver.switch_to_window(window_overviewpage)
                    # Check if we're on the overview page:
                    try:
                        results_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "resultsContainer")))
                        logger.debug('Back on overviewpage {}'.format(number_overviewpage))
                    except TimeoutException as ex:
                        logger.error('Results section not found for overview page {}'.format(number_overviewpage))
                    sleep(5)
                    number_hotelpage += 1

            except TimeoutException as ex:
                logger.error('ERROR: results section not found for overview page {}, with '.format(number_overviewpage))
                logger.error('Exception:'+str(ex))

            # going to the next page, however, not when on the last page
            if number_overviewpage == last_page:
                logger.debug('This was the last page, breaking now.')
                break
            elif number_overviewpage >= self.MAXPAGES:
                logger.debug('We have reached the maximum defined overview pages, breaking now.')
                break
            else:
                next_page = driver.find_element_by_class_name('pagination-next')
                next_page.click()
                logger.debug('Retrieved all information from the overview page')
                logger.debug('Going to the next page')
                sleep(3)
            number_overviewpage += 1
            
        logger.debug('We have fetched all the overviewpages that exist (or the max number of pages defined).')

        driver.quit()

        





