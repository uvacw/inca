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

    def __init__(self,database=True, maxfora = 2, maxpages=2, maxthreads=2):
   
        self.database = database
        self.START_URL = "http://www.voedingsforum.nl/"
        self.BASE_URL = "http://www.voedingsforum.nl/"
        self.MAXPAGES = maxpages
        self.MAXTHREADS = maxthreads
        self.MAXFORA = maxfora
        
    def get(self):
        '''                                                                             
        Fetches articles from Voedingsforum
        '''
        self.doctype = "voedingsforum (health)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=12, day=8)

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

        allfora = []
        
        
        current_url = self.START_URL
# you are redirected to a cookiewall _unless_ a cookie with the key cookieAccept and the value is True is send to the server
# we found that out by inspecting the source code of the cookiewall page to which we were redirected: we examined the javascript-code in there, and the central functionality seemed to be that it created such a cookie. 
# We can do so manually by simply providing a python dict:
        overview_page = requests.get(current_url, cookies = {'cookieAccept':'True'})
        tree = fromstring(overview_page.text)
        linkobjects = tree.xpath('//table//b/a')
        links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
        links = links[0:self.MAXFORA]
        logger.debug("Er zijn {} links".format(len(links)))
        logger.debug("\n".join(links))
        for link in links:
            currentforum = {}
            currentforum['url'] = link
            # TODO: naam van forum scrapen
            # currentforum['name'] = 'Afvallen en aankomen' (of zoiets, met XPATH scrapen)
            currentforum['threads'] = []
            page = 1
            current_page = link
            sleep(randrange(5,10))
            overview_pagesub = requests.get(current_page, cookies = {'cookieAccept' : 'True'})
# if we want to save the page for test purposes:
             #with open('/home/chamoetal/Desktop/voedingtest.html', mode = 'w') as fo:
                 #fo.write(overview_page.text)
            logger.debug('ik ga nu {} ophalen'.format(link))
# De loop wordt gestopt door te checken of de pagina de tekst hieronder bevat.
            while overview_pagesub.content.find(b'Foutmelding' and b'Geen onderwerpen gevonden') == -1:
                logger.debug('de huidige pagina bevat geen foutmelding')
                tree_sub = fromstring(overview_pagesub.text)
                sublinkobjects = tree_sub.xpath('//table//table//tr/td/a[not(@onmouseout)]/@href')
                logger.debug('this page has {} sublinkobjects'.format(len(sublinkobjects)))
                sublinks  = [self.BASE_URL+ li for li in sublinkobjects]
                logger.debug("\n".join(sublinks))
                for sublink in sublinks:
                    currentthread = {}
                    currentthread['posts'] = []
                    # TODO: we willen ook nog een aantal keys erbij, met name titel en aantal keer gelezen
                    pagesub = 1
                    logger.debug('ik ga nu {} ophalen'.format(sublink))
                    sleep(randrange(5,10))
                    this_page = requests.get(sublink)
                    while True:
                        treesub = fromstring(this_page.text)
                        thread = treesub.xpath('//table//span[@id="msg"]')
                        messages = [t.text_content() for t in thread]
                        messages = [b.strip() for b in messages]
                        postlijst = []
                        for message in messages:
                            if len(message)>0:
                                postlijst.append({'post':message})
#User information - extracting from the elements. Username and level come together in one list, country of origin and amount of messages in a second list

                        user_elem = treesub.xpath('//*[@class="topiclight" or @class="topicdark"]')
                        # TODO: voor de zekerheid checken of len(user_elem) == aantal posts
                        ii = 0
                        for user in user_elem:
                            userinfo = user.getchildren()
                            if len(userinfo) == 2:
                                userleveltemp = userinfo[0].text_content().replace("\r\n", " ") .replace("                 ", " ") .replace("  ", "")
                                # username_temp.append(userleveltemp.split(" ")[0])
                                # TODO: de volgende regel ook voor land etc
                                postlijst[ii]['username'] = userleveltemp.split(" ")[0]
                                postlijst[ii]['userlevel'] = userleveltemp.split (" ")[1]
                                # level_temp.append(userleveltemp.split (" ")[1])
                                                            
                                countryamounttemp = userinfo[1].text_content().replace ("Berichten", " ") .replace("\r\n", " ") .replace ("\t\t", "") .replace("                  ", " ") .replace ("   ", " ")

                                thiscountrystring = "".join(re.findall(r"[A-Za-z]", countryamounttemp))
                                if thiscountrystring == "":
                                    postlijst[ii]['usercountry'] ='NA'
                                else:
                                    postlijst[ii]['usercountry'] = thiscountrystring

                                postlijst[ii]['useramountofposts'] = int("".join(re.findall(r"[0-9]", countryamounttemp)))
           
                            else:
                                continue
                            ii+=1


                        pagesub+=1
                        if pagesub > self.MAXTHREADS:
                            break
                        next_url = sublink+'&whichpage='+str(pagesub)
                        sleep(randrange(5,10))
                        next_page = requests.get(next_url)
                        logger.debug('ik ga nu {} ophalen'.format(next_url))
                        if next_page.content.find(b'/_lib/img/icon_user_profile')==-1:
                            logger.debug('pagina bestaat niet; ik stop ermee')
                            break
                        else:
                            this_page = next_page
                    currentthread['posts'] = postlijst
                    #currentthread['messages'] = post
                    #currentthread['users'] = country_temp
                    # TODO: OOK NOG REST
                    # TODO: dicts in plaats van lange lijsten
                    # dus niet een lijst met lengte 10 van alle posts en nog eentje met alle users
                    # maar slechts EEN lijst van dicts, dus zoiets:
                    # [{'message':'bla bla', 'user':'damian', country:'nl'}, {'message':'nog eentje' ...

                    currentforum['threads'].append(currentthread)
                page+=1
                if page > self.MAXPAGES:
                    break
                current_page = link+'&sortfield=lastpost&sortorder=desc&whichpage='+str(page)
                sleep(randrange(5,10))
                overview_pagesub = requests.get(current_page)
                logger.debug('ik ga nu {} ophalen'.format(current_page))
          
                
            allfora.append(currentforum)
            
        return allfora
