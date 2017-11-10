import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange
import re

logger = logging.getLogger(__name__)

logger.setLevel('DEBUG')




# Multipage non-rss scraper. Wanneer een niet-bestaande URL wordt opgevraagd wordt een foutmelding weergeven. De loop stopt zodra deze foutmelding gevonden wordt.
class voedingsforum(Scraper):
    """Scrapes Voedingsforum"""

    def __init__(self,database=True, maxfora=2, maxthreads=2):
   
        self.database = database
        self.START_URL = "http://www.voedingsforum.nl/"
        self.BASE_URL = "http://www.voedingsforum.nl/"
        self.MAXFORA = maxfora
        self.MAXTHREADS = maxthreads
        
    def get(self):
        '''                                                                             
        Fetches articles from Voedingsforum
        '''
        self.doctype = "voedingsforum (health)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)

        posts = []
        posts_temp = []
        username_temp = []
        username = []
        level_temp = []
        level = []
        country_temp = []
        country = []
        amount_temp = []
        amount = []

        page = 1
        current_url = self.START_URL
         # you are redirected to a cookiewall _unless_ a cookie with the key cookieAccept and the value is True is send to the server
        # we found that out by inspecting the source code of the cookiewall page to which we were redirected: we examined the javascript-code in there, and the central functionality seemed to be that it created such a cookie. 
        # We can do so manually by simply providing a python dict:
        overview_page = requests.get(current_url, cookies = {'cookieAccept':'True'})
        tree = fromstring(overview_page.text)
        linkobjects = tree.xpath('//table//b/a')
        links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
        logger.debug("Er zijn {} links".format(len(links)))
        logger.debug("\n".join(links))
        for link in links:
            current_page = link
            sleep(randrange(5,10))
            overview_pagesub = requests.get(current_page, cookies = {'cookieAccept' : 'True'})
             # if we want to save the page for test purposes:
             #with open('/home/chamoetal/Desktop/voedingtest.html', mode = 'w') as fo:
                 #fo.write(overview_page.text)
            logger.debug('ik ga nu {} ophalen'.format(link))
            # De loop wordt gestopt door te checken of de pagina de tekst hieronder bevat.
            while overview_pagesub.content.find(b'Foutmelding') == -1:
                logger.debug('de huidige pagina bevat geen foutmelding')
                tree_sub = fromstring(overview_pagesub.text)
                sublinkobjects = tree_sub.xpath('//table//table//tr/td/a[not(@onmouseout)]/@href')
                logger.debug('this page has {} sublinkobjects'.format(len(sublinkobjects)))
                sublinks  = [self.BASE_URL+ li for li in sublinkobjects]
                for sublink in sublinks:
                    pagesub = 1
                    logger.debug('ik ga nu {} ophalen'.format(sublink))
                    sleep(randrange(5,10))
                    this_page = requests.get(sublink)
                    while True:
                        treesub = fromstring(this_page.text)
                        thread = treesub.xpath('//table//span[@id="msg"]')
                        messages = [t.text_content() for t in thread]
                        messages = [b.strip() for b in messages]
                        
#User information - extracting from the elements. Username and level come together in one list, country of origin and amount of messages in a second list
                                              
                        user_elem = treesub.xpath('//*[@class="topiclight" or @class="topicdark"]')
                        for user in user_elem:
                            userinfo = user.getchildren()
                            if len(userinfo) == 2:
                                userleveltemp = userinfo[0].text_content().replace("\r\n", " ") .replace("                 ", " ") .replace("  ", "")
                                username_temp.append(userleveltemp.split(" ")[0])
                                level_temp.append(userleveltemp.split (" ")[1])
                                                            
                                countryamounttemp = userinfo[1].text_content().replace ("Berichten", " ") .replace("\r\n", " ") .replace ("\t\t", "") .replace("                  ", " ") .replace ("   ", " ")
                                
                                countrytemp = "".join(re.findall(r"[A-Za-z]", countryamounttemp))
                                if countrytemp == "":
                                    country_temp.append("NA")
                                else:
                                    country_temp.append(countrytemp)

                                amount_temp.append("".join(re.findall(r"[0-9]", countryamounttemp)))
           
                            else:
                                continue

                        posts_temp.append(messages)
                        
                        logger.debug(posts_temp)
                        logger.debug(username_temp)
                        logger.debug(level_temp)
                        logger.debug(country_temp)
                        logger.debug(amount_temp)

                        pagesub+=1
                        if pagesub > self.MAXTHREADS:
                            break
                        next_url = sublink+'?whichpage='+str(pagesub)
                        logger.debug('ik ga nu {} ophalen'.format(next_url))
                        sleep(randrange(5,10))
                        next_page = requests.get(next_url)
                        if next_page.content.find(b'@href="pop_profile"') == -1:
                            logger.debug('pagina bestaat niet; ik stop ermee')
                            break
                        else:
                            this_page = next_page
                    posts.append(posts_temp)
                    username.append(username_temp)
                    level.append(level_temp)
                    country.append(country_temp)
                    amount.append(amount_temp)
            page+=1
            if page > self.MAXPAGES:
                break
            
            current_url = self.START_URL+'?whichpage='+str(page)
            overview_page = requests.get(current_url)


        allforum = {"messages": posts,
                    "username": username,
                    "level": level,
                    "country": country,
                    "amount": amount}
        return allforum
