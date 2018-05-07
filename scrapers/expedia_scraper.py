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

        driver = webdriver.Firefox(executable_path=r'/home/lisa/INCA/inca/geckodriver')
        driver.get("https://www.expedia.com")
        
        hotelsonly = driver.find_element_by_id("tab-hotel-tab-hp") 
        hotelsonly.click()
        sleep(3)
        destination = driver.find_element_by_id("hotel-destination-hp-hotel")
        destination.send_keys('Amsterdam')#(self.CITYNAME) 
        destination.send_keys(Keys.RETURN)
        sleep(10)

        hotel_dicts = []

        # Check how many hotels there are to find the last overview page:
        page_indicator = driver.find_elements_by_class_name("showing-results")[0].text
        amount_hotels_total = [int(s) for s in page_indicator.split() if s.isdigit()][-1]
        last_page = math.ceil(amount_hotels_total/50)

        # Get all the elements from each overview page:
        # check whether the 'next page' button is available in a while loop
        number_overviewpage = 1
        onlastpage = 0
        window_overviewpage = driver.window_handles[0]
        while onlastpage == 0:
            # Check how many reviews there are
            page_indicator = driver.find_elements_by_class_name("showing-results")[0].text
            amount_hotels_current = [int(s) for s in page_indicator.split() if s.isdigit()][-2]
            # Check whether this page is not above the maximum defined overview pages;
            # or if it is the last page
            if number_overviewpage > 2:#self.MAXPAGES:
                print("The overview page ({}) is above the max defined pages, so we're breaking".format(number_overviewpage))
                break
            elif number_overviewpage == last_page:
                print('On the last overview page ({})'.format(number_overviewpage))
            else:
                print('On overview page {}/{}'.format(number_overviewpage,last_page))
            try:
                results_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "resultsContainer")))
                print('Results section found')
                # Find all article elements:
                hotels = driver.find_elements_by_css_selector('section article')
                # Find all sponsored article elements:
                sponsored_hotels = driver.find_elements_by_css_selector('section [id$=sponsored]')
                print('There are {} hotels on this overviewpage, of which {} are sponsored hotels.'.format(len(hotels),len(sponsored_hotels)))
                # Length of articles should be 50 (without sponsored articles)
                if len(hotels)-len(sponsored_hotels) > 50:
                    print('List of hotels is longer than 50, there are probably {} banner(s) or decoy(s) in the list.'.format(len(hotels)-len(sponsored_hotels)-50))
                    n = 0
                    banner = -1
                    for hotel in hotels:
                        if hotel.get_attribute("id") == 'MODBanner':
                            print('Found a banner, it is the {}th item'.format(n))
                            banner = n
                        n += 1
                    if banner == -1:
                        print('OOPS, no banner was found! The length is still {}'.format(len(hotels)))
                    # remove these elements from the list!!!
                    del hotels[(banner)]
                    if len(hotels)-len(sponsored_hotels) == 50:
                        print('The final list of hotels now contains 50 hotels, without sponsored hotels')
                    else:
                        print('OOPS, the final list of hotels contains {} hotels'.format(len(hotels)-len(sponsored_hotels)))
                # Find the link elements for each hotel:
                hotel_urls_buttons = []
                hotel_urls = []
                for hotel in hotels:
                    url_button = hotel.find_element_by_css_selector('.flex-link')
                    url = hotel.find_element_by_css_selector('.flex-link').get_attribute('href')
                    hotel_urls_buttons.append(url_button)
                    hotel_urls.append(url)
                    # Find hotels with external links (and deal with in a different way):
                        external_url = hotel.find_element_by_css_selector('.flex-link').get_attribute('data-externalurl')
                assert len(hotels) == len(hotel_urls) == len(hotel_urls_buttons)
                print('For each hotel a link was found.')
                print('There are {} links'.format(len(hotels)))

                # Create a generator for hotel links:
                hotel_urls_gen = (e for e in hotel_urls_buttons)
                # Go to each hotel link on this page:
                number_hotelpage = 1
                for i in range(len(hotel_urls_buttons)):
                    # IF THE PAGE CONTAINS AN EXTERNAL URL, THAN DON'T CLICK!
                    this_url = next(hotel_urls_gen)
                    this_url.click()
                    window_hotelpage = driver.window_handles[1]
                    driver.switch_to_window(window_hotelpage)
                    print('On hotel page {}/{} of overview page {}/{}'.format(number_hotelpage,len(hotel_urls),number_overviewpage,last_page))
                    try:
                        hotel_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "price-compare-list")))
                        print('Hotel information section found')
                    except TimeoutException as ex:
                        print('ERROR: hotel information section not found for this hotel {} with error:'.format(number_hotelpage,str(ex)))
                    # Take information from the page:
                    name = driver.find_element_by_css_selector('#hotel-name').text
                    stars = driver.find_element_by_css_selector('.star-rating-wrapper').text
                    rating = float(driver.find_element_by_css_selector('.rating-scale').text.split(' ')[0])
                    review_quantity = int(driver.find_element_by_css_selector('#link-to-reviews > span').text)
                    # Add all information to a dict:
                    thishotel = {'url':hotel_urls[i].strip(),
                                 'id':i,
                                 'name':name.strip(),
                                 'stars':stars.strip(),
                                 'rating':rating,
                                 'review_quantity':review_quantity,
                                 'review':[]}
                    print(thishotel.keys())
                    print('Retrieved all information from the hotel page')

                    # Go to the review element
                    link = driver.find_element_by_css_selector('#link-to-reviews')
                    link.click()
                    try:
                        results_section = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, "review-summary")))
                        print('Review section found')
                    except TimeoutException as ex:
                        print('ERROR: Review section not found for this hotel: {}'.format(number_hotelpage))

                    # Gather information from the reviews
                    subratings_elements = driver.find_elements_by_css_selector('.dimensions > div')
                    subratings = {}
                    for sub in subratings_elements:
                        rating, category = sub.text.split(" ",1)
                        subratings[category] =  rating
                    thishotel['subratings'] = subratings
                    
                    reviews = driver.find_elements_by_css_selector('#reviews > article')
                    # length should be 10, but not for last page
                    #for review in reviews:
                        
                    
                    # Close the window and focus back on the overview page
                    driver.close()
                    driver.switch_to_window(window_overviewpage)
                    # Check if we're on the overview page:
                    try:
                        results_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "resultsContainer")))
                        print('Back on overviewpage {}'.format(number_overviewpage))
                    except TimeoutException as ex:
                        print('ERROR: results section not found for overview page {}'.format(number_overviewpage))
                    sleep(5)
                    #hotel_dicts.append(thishotel)
                    number_hotelpage += 1
                    yield thishotel
        
            except TimeoutException as ex:
                print('ERROR: results section not found for overview page {}'.format(number_overviewpage))
                print('Exception:'+str(ex))

            # going to the next page, however, not when on the last page
            if number_overviewpage == last_page:
                ('This was the last page, breaking now.')
                break
            else:
                next_page = driver.find_element_by_class_name('pagination-next')
                next_page.click()
                print('Retrieved all information from the overview page')
                print('Going to the next page')
                sleep(5)
            number_overviewpage += 1
            
        print('We have fetched all the overviewpages that exist (or the max number of pages defined).')

        driver.quit()

        #return hotel_dicts

        





