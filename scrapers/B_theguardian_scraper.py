import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange

'''
NOTES: First letter problem, might be unsolvable e.g. https://www.theguardian.com/politics/2016/jun/01/british-asians-views-eu-referendum-figures-brexit . 
'''

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

class theguardian(Scraper):
    """Scrapes The Guardian pages"""
    
    def __init__(self,database=True, starturl = "https://www.google.nl/search?q=site%3Ahttps%3A%2F%2Fwww.theguardian.com%2F&oq=site%3Ahttps%3A%2F%2Fwww.theguardian.com%2F&aqs=chrome..69i57j69i58.2212j0j7&sourceid=chrome&ie=UTF-8"):
        self.database = database
        self.START_URL = starturl
        self.BASE_URL = "www.theguardian.com"          

    def get(self):
        '''Fetches articles from theguardian.com'''
        self.doctype = "The Guardian links"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=10, day=20)
        
        allurls = []
        articles = []
        articles_enriched = []
        
        starturl = "https://www.google.nl/search?q=Brexit+site%3Ahttps%3A%2F%2Fwww.theguardian.com%2F&source=lnt&tbs=cdr%3A1%2Ccd_min%3A{}%2F{}%2F{}%2Ccd_max%3A{}%2F{}%2F{}&tbm="
        
        '''Date stuff (NOT TO BE USED UNTIL SCRAPER COMLETE)'''
        start = datetime.datetime.strptime("06/01/2016", "%m/%d/%Y")
        end = datetime.datetime.strptime("06/03/2016", "%m/%d/%Y")
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
        
        visited = []

        for d in date_generated:
            allurls.append(starturl.format(d.month, d.day, d.year, d.month, d.day, d.year))
        allurlsgen = (e for e in allurls)
        
        '''Creates for loop to cycle through dates and obtain overviews'''
        for thisurl in allurlsgen:
            sleep(randrange(5,10))
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
            overview_page = requests.get(thisurl, headers=headers)

            visited.append(thisurl)
            tree = fromstring(overview_page.text)

            logger.debug("Fetched the overviewpage: {}".format(thisurl))
            # the while loop ensures that we stop once we get an empty page
            while True:
                linkselement = tree.xpath("//*[@class='r']/a")
                links = [e.attrib["href"] for e in linkselement if "href" in e.attrib]
                url_title = tree.xpath("//*[@class='r']//text()")

                assert len(links)==len(url_title)

                for i in range(len(links)):
                    thisarticle = {'link':links[i].strip(),
                                 'url_title':url_title[i].strip()}
                    articles.append(thisarticle)
                # apart from the initial while-loop condition, we also
                # stop the loop once we reach the maximum number of
                # pages defined before:

                try:
                    altnext_url = tree.xpath("//*[@id='pnnext']")[0].attrib['href']

                except:
                    logger.debug('There does not seem to be a next page:' )
                    break

                next_url = "https://www.google.nl"+altnext_url

                if next_url in visited:
                    logger.debug('We have been here before, let\'s stop.')
                    break

                logger.debug('There is more than one page, we will move to {}'.format(str(next_url)))
                sleep(randrange(5,10))
                visited.append(next_url)

                overview_page = requests.get(next_url, headers=headers)
                tree = fromstring(overview_page.text)
                logger.debug("Fetched the overviewpage: {}".format(next_url))

        '''Article specific pages'''        
        logger.debug('We have fetched all overviewpages that exist. There are {} articles in total'.format(len(articles)))
        for article in articles:
            link = article['link']
            logger.debug(article)
            logger.debug('Fetched the article-specific webpage: {}'.format(link))
            sleep(randrange(5,10))
            current_page = requests.get(link)
            
            if len(current_page.text)<1:
                logger.warning("this seems to be an empty page")
                continue
                
            tree = fromstring(current_page.text)
                
            try:        
                title = tree.xpath("//*[@class='content__headline']/text()")[0]
            except:
                title = ""
                logger.info("No 'title' field encountered - don't worry, maybe it just doesn't exist.")  
                continue
            try:        
                teaser = tree.xpath("//*[@class='content__standfirst']/p/text()")[0]
            except:
                teaser = ""
                logger.info("No 'teaser' field encountered - don't worry, maybe it just doesn't exist.")  
            try:
                text = " ".join(tree.xpath("//*[@itemprop='articleBody']/p/text()|//*[@itemprop='articleBody']//a/text()"))
            except:
                text = ""
                logger.info("{} did not have text. Problem?".format(link))
            try:
                date = " ".join(tree.xpath("//*[@class='content__dateline']/time[1]/text()"))
            except:
                date = ""
                logger.info("No 'date' field encountered. That's weird. Check it.")

            articleinfo = article
            article.update({"title":title.replace("\n","").strip(),
                            "teaser":teaser.strip(),
                            "text":text.replace("\\","").replace("\n","").strip(),
                            "date":date.replace("\n","").strip()
                           })
            
            if article['text'] == "" and article['teaser'] == "" and article['title'] == "" and article['date'] == "":
                pass
            else:
                articles_enriched.append(articleinfo)

        logger.debug('We have fetched all articles from the article-specific webpage that exist. There are {} articles in total'.format(len(date)))
        return articles_enriched