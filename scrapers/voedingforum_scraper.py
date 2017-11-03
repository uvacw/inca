import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange

logger = logging.getLogger(__name__)

logger.setLevel('DEBUG')




# Multipage non-rss scraper. Wanneer een niet-bestaande URL wordt opgevraagd wordt een foutmelding weergeven. De loop stopt zodra deze foutmelding gevonden wordt.
class voedingsforum(Scraper):
    """Scrapes Voedingsforum"""

    #def __init__(self,database=True):
    def __init__(self,database=True, maxpages=2, maxsubpages=2, maxthread=2):
   
        self.database = database
        self.START_URL = "http://www.voedingsforum.nl/"
        self.BASE_URL = "http://www.voedingsforum.nl/"
        self.MAXPAGES = maxpages
        self.MAXSUBPAGES = maxsubpages
        self.MAXTHREAD = maxthread

    def get(self):
        '''                                                                             
        Fetches articles from Voedingsforum
        '''
        self.doctype = "voedingsforum (health)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=10, day=20)

        posts = []
        posts_temp = []



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
                if page > self.MAXSUBPAGES:
                    break
                tree_sub = fromstring(overview_pagesub.text)
                sublinkobjects = tree_sub.xpath('//table//table//tr/td/a[not(@onmouseout)]/@href')
                logger.debug('this page has {} sublinkobjects'.format(len(sublinkobjects)))
                sublinks  = [self.BASE_URL+ li for li in sublinkobjects]
                for sublink in sublinks:
                    pagesub = 1
                    logger.debug('ik ga nu {} ophalen'.format(sublink))
                    if pagesub > 1:
                        break
                    sleep(randrange(5,10))
                    this_page = requests.get(sublink)
                    while True:
                        treesub = fromstring(this_page.text)
                        thread = (treesub.xpath('//table//span[@id="msg"]'))
                        messages = [t.text_content() for t in thread]
                        messages = [b.strip() for b in messages]
#User information - extracting from the elements. Username and level come together in one list, country of origin and amount of messages in a second list
                        username_level = []
                        country_amount = []
                        user_elem = treesub.xpath('//*[@class="topiclight" or @class="topicdark"]')
                        for user in user_elem:
                            userinfo = user.getchildren()
                            if len(userinfo) == 2:
                                username_level.append(userinfo[0].text_content())
                                country_amount.append(userinfo[1].text_content())
                            else:
                                continue

                                               
                        logger.debug(messages)
                        logger.debug(username_level)
                        logger.debug(country_amount)

                        posts_temp.append({'messages': messages})
                        
                        pagesub+=1
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
            page+=1
            current_url = self.START_URL+'?whichpage='+str(page)
            overview_page = requests.get(current_url)
        return posts
