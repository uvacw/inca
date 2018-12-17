from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from urllib import parse
import datetime
from ..core.scraper_class import Scraper
import time
import requests
import logging
from lxml.html import fromstring

logger = logging.getLogger("INCA")

scraper = Scraper()

class junknews_scraper(Scraper):

    def __init__(self):

        self.doctype = "junknews_scraper"
        self.START_URL = "https://newsaggregator.oii.ox.ac.uk/news/app/"
        self.version = ".1"
        self.datetime = datetime.datetime(year=2018, month=11, day=28)

    def get(self, save, hours, *args, **kwargs):

        """
        Gets junk news articles from Oxford Internet Institute's Junk News Aggregator
        hours = the number of previous hours to be scraped. Options include:
        1,2,3,6,9,12,24,48,72,168 (1 week), 720 (1 month).
        """
        
        """ Find publishers, websites and facebooksites  """

        options = Options()
        options.set_headless(True)
        driver = webdriver.Firefox(options = options)
        driver.get(self.START_URL)
        time.sleep(5)
        hours_xpath = '//*[@value="{}"]'.format(hours)
        driver.find_element_by_xpath(hours_xpath).click()
        time.sleep(5)

        x = driver.find_elements_by_xpath('//a[@class="link-website"]') # Urls
        fb = driver.find_elements_by_xpath('//a[@class="link-facebook"]') # FBsites
        y = driver.find_elements_by_xpath('//span[@class="publisher"]') # Publishers

        publishers = []
        for i in y:
            publishers.append(i.text) 

        url = []
        for i in x: 
            url.append(str(i.get_attribute("href")))

        facebooksites = []
        for i in fb: 
            facebooksites.append(str(i.get_attribute("href")))

        driver.close()
        
        """ Get newssources and htmltrees, combine lists into a dict """
   

        def getnewssource(webpage):
            newssource = parse.urlsplit(webpage).netloc
            if newssource.startswith("www."):
                newssource = newssource[4:]
            sep = '.'
            newssource = newssource.split(sep, 1)[0]
            return newssource
 
        def gettree_chicks(webpage):
            options = Options()
            options.set_headless(True)
            driver = webdriver.Firefox(options = options)
            driver.get(webpage)
            time.sleep(15)
            try:
                driver.find_element_by_xpath('//button[@class="button_button intro_acceptAll "]').click()
            except:
                pass
            tree=driver.page_source
            driver.close()
            return(tree)

        def gettree(webpage):
            if webpage.startswith("https://www.facebook.com/"):
                print("Facebook-post.")
                return("Facebook-post")
            elif webpage.startswith("https://www.chicksonright.com/"):
                tree = gettree_chicks(webpage)
                return(tree)
            else:
                header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}
                r = requests.get(webpage, headers=header)
                if r.status_code==200:
                    tree = r.text
                    print("Retrieved html-tree.")
                    return(tree)
                else:
                    mystring = "Retrieving html of " + i + " gave the error code: " + str(r.status_code)
                    print(mystring)
                    return('NaN') #Or mystring?

        newssources = []
        for a in url:
            newssources.append(getnewssource(a))

        trees_data = []
        for i in url:
            trees_data.append(gettree(i))

        all_data = [{'url': w, 'publisher': p, 'newssource': n, 'facebooksite': f, 'htmltree': t} for w, p, n, f, t in zip(url, publishers, newssources, facebooksites, trees_data)]

    
        """ General function for extracting article text """


        def getarticle(s, chunck, element, name):
            article = s.find(chunck, {element : name}).findAll('p')
            entrycontent = ""
            for element in article:
                entrycontent += '\n'  + ' ' + ' '.join(element.findAll(text = True))
            return entrycontent


        """ A parser function for each website """


        def bigleaguepolitics(soup):
            title = soup.h1.text
            soup = soup.find("div", {"id": "mvp-content-main"})
            try:
                soup.find('span', class_="mostpopular-title").decompose()
            except:
                pass
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = soup.get_text()
            entrycontent = entrycontent.replace('\nTrending: \n','')
            sep = "Share Tweet"
            entrycontent = entrycontent.split(sep, 1)[1]
            sep2 = "Bypass Tech Censorship!"
            entrycontent = entrycontent.split(sep2, 1)[0]
            return{"title":title, "text":entrycontent, "function":"bigleaguepolitics"}

        def bizpacreview(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            sep = "We know first-hand that censorship against conservative news is real"
            entrycontent = entrycontent.split(sep, 1)[0]
            return{"title":title, "text":entrycontent, "function":"bizpacreview"}

        def breitbart(soup):
            title = soup.xpath("//h1")[0]
            title = soup.xpath("//h1")[0].text_content()
            entrycontent = soup.find_class("entry-content")[0] 
            entrycontent = entrycontent.text_content()
            return{"title":title, "text":entrycontent, "function":"breitbart"}
        """ Follow xxxx on Twitter/You can follow him on Twitter
            Should be deleted, or does it matter? """

        def canadafreepress(soup): 
            title = soup.h1.text
            article = soup.find_all('div', {'style': 'clear:both;'})
            for element in article:
                for script in element(["script", "style"]):
                    script.extract()
            entrycontent = ""
            for element in article:
                element.findAll('p')
                entrycontent += '\n' + ' '.join(element.findAll(text = True))
            return{"title":title, "text":entrycontent, "function":"canadafreepress"}

        def chicksonright(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "td-post-content")
            entrycontent = entrycontent.replace('Email address','')
            entrycontent = entrycontent.replace('This is a modal window.','')
            tweet_ids = []
            for element in soup.find_all("twitter-widget"):
                tweet_id = element["data-tweet-id"]
                tweet_ids.append(tweet_id)
            if len(tweet_ids) == 0:
                return{"title":title, "text":entrycontent, "function":"chicksonright"}
            else:
                return{"title":title, "text":entrycontent, "tweet_ids" : tweet_ids, "function":"chicksonright"}

        def cnsnews(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "field-items")
            return{"title":title, "text":entrycontent, "function":"cnsnews"}

        def conspiracydailyupdate(soup): 
            title = soup.find("h1", {"class":  "entry-title"}).text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return{"title":title, "text":entrycontent, "function":"conspiracydailyupdate"}
        """ Note! Most often no text, just links to other websites """

        def dailycaller(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "id", "ob-read-more-selector")
            sep = "Content created by The Daily Caller News Foundation is available without charge"
            entrycontent = entrycontent.split(sep, 1)[0]
            return{"title":title, "text":entrycontent, "function":"dailycaller"}

        def dailywire(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "field-body")
            return{"title":title, "text":entrycontent, "function":"dailywire"}

        def davidharrisjr(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "vw-post-content clearfix")
            sep = 'To stay up to date with David’s No Nonsense News'
            entrycontent = entrycontent.split(sep, 1)[0]
            return{"title":title, "text":entrycontent, "function": "davidharrisjr"}

        def envolve(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "itemprop", "articleBody")
            return{"title":title, "text":entrycontent, "function":"envolve"}

        def gellerreport(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            sep = "Your contribution supports independent journalism"
            entrycontent = entrycontent.split(sep, 1)[0]
            return{"title":title, "text":entrycontent, "function":"gellerreport"}

        def hotair(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "col-xs-12 article-text")
            return{"title":title, "text":entrycontent, "function":"hotair"}

        def legalinsurrection(soup):
            title = soup.find("h2", {"class":  "postTitle"}).text
            entrycontent = getarticle(soup, "div", "class", "postContent")
            return{"title":title, "text":entrycontent, "function":"legalinsurrection"}

        def lifenews(soup):
            title = soup.h2.text
            entrycontent = getarticle(soup, "div", "class", "article")
            entrycontent = entrycontent.replace('ADVERTISEMENT','')
            return{"title":title, "text":entrycontent, "function":"lifenews"}

        def lifezette(soup):
            title = soup.h1.text
            subtitle = soup.h2.text
            soup = soup.find("div", {"class":"text font-default font-size-med"})
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = subtitle + soup.get_text()
            entrycontent = entrycontent.replace('Advertisement','')
            return{"title":title, "text":entrycontent, "function":"lifezette"}

        def naturalnews(soup):
            title = soup.find("h1", {"class":  "entry-title"}).text
            entrycontent = soup.find("div", {"class":  "entry-content"}).text
            return{"title":title, "text":entrycontent, "function":"naturalnews"}

        def newrightnetwork(soup):
            title = soup.h1.text
            entrycontent = soup.find("div", {"class":  "mtl-post-content"}).text
            return{"title":title, "text":entrycontent, "function":"newrightnetwork"}

        def nworeport(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "post-content")
            return{"title":title, "text":entrycontent, "function":"nworeport"}

        def palmerreport(soup):
            title = soup.h1.text
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = getarticle(soup, "div", "class", "fl-post-content clearfix")
            return{"title":title, "text":entrycontent, "function":"palmerreport"}

        def pjmedia(soup):
            title = soup.h3.text
            entrycontent = getarticle(soup, "div", "class", "pages")
            return{"title":title, "text":entrycontent, "function":"pjmedia"}
    
        def rawstory(soup):
            title = soup.find("h1", {"class":  "blog-title"}).text
            entrycontent = getarticle(soup, "div", "class", "blog-content https-content")
            return{"title":title, "text":entrycontent, "function":"rawstory"}

        def redstate(soup):
            title = soup.h1.text
            try:
                soup.find('div', class_="small-card-bottom").decompose()
            except:
                pass
            soup = soup.find("div", {"class": "col-xs-12 article-text"})
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = soup.get_text()
            sep = "Share on Facebook"
            entrycontent = entrycontent.split(sep, 1)[0]
            return{"title":title, "text":entrycontent, "function":"redstate"}

        def rushlimbaugh(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return{"title":title, "text":entrycontent, "function":"rushlimbaugh"}
    
        def shareblue(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "td-post-content")
            return{"title":title, "text":entrycontent, "function":"shareblue"}

        def theblaze(soup):
            title = soup.h1.text
            try:
                subtitle = soup.h2.text
            except:
                subtitle = ""
            entrycontent = subtitle + '\n' + soup.find("div", {"class": "body-description"}).text
            return{"title": title, "text": entrycontent, "function": "theblaze"}

        def thefederalist(soup): 
            title = soup.h2.text
            subtitle = soup.find("div", {"class": "subtitle"}).text
            entrycontent = subtitle
            for element in soup.select("div[class*=entry-content]"):
                entrycontent += '\n' + ' '.join(element.findAll(text = True))
            return{"title":title, "text":entrycontent, "function":"thefederalist"}

        def thegatewaypundit(soup):
            title = soup.h2.text
            try:
                subtitle = soup.h3.text
            except:
                subtitle = ""
            entrycontent = subtitle + '\n' + getarticle(soup, "div", "class", "clearfix")
            sep = "As a privately owned web site"
            entrycontent = entrycontent.split(sep, 1)[0]
            return{"title":title, "text":entrycontent, "function": "thegatewaypundit"}

        def thepoliticalinsider(soup):
            title = soup.find("header", {"class":  "article-header row"}).text
            entrycontent = soup.find("div", {"id": "article-body"}).text
            return{"title":title, "text":entrycontent, "function":"thepoliticalinsider"}
 
        def therightscoop(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return{"title":title, "text":entrycontent, "function": "therightscoop"}

        def truepundit(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "itemprop", "articleBody")
            return{"title": title, "text":entrycontent, "function":"truepundit"}

        def twitchy(soup):
            title = soup.h1.text
            soup = soup.find("div", {"class":"col-xs-9 article-text"})
            for item in soup.findAll("div", {"class":"home-trending-widget-article"}):
                item.extract() 
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = soup.get_text()
            sep = "Share on Facebook\n"
            entrycontent = entrycontent.split(sep, 1)[0] 
            return{"title":title, "text":entrycontent, "function":"twitchy"}

        def westernfreepress(soup):
            title = soup.h1.text
            soup.find('ul', class_="essb_links_list").decompose()
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            if len(entrycontent) > 0:
                return{"title":title, "text":entrycontent, "function":"westernfreepress"}
            else:
                return fallback(soup)

        def wnd(soup):
            title = soup.h1.text
            try:
                entrycontent = getarticle(soup, "div", "class", "entry-content wnd")
                return{"title":title, "text":entrycontent, "function":"wnd"}
            except:
                entrycontent = getarticle(soup, "div", "class", "entry-content non-wnd")
                return{"title":title, "text":entrycontent, "function":"wnd"}

        def zerohedge(soup):
            title = soup.find("h1", {"class": "page-title"}).text
            entrycontent = getarticle(soup, "div", "class", "node__content")
            return {"title":title,"text": entrycontent, "function": "zerohedge"}

        def fallback(soup):
            print("Fallback-method.")
            title = "NaN"
            for script in soup (["script", "style"]):
                script.extract()
            entrycontent = soup.get_text()
            lines = (line.strip() for line in entrycontent.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            entrycontent = '\n'.join(chunk for chunk in chunks if chunk)
            return{"title":title, "text":entrycontent, "function": "fallback"}

 
        """ Mapping functions to newssources """
 

        mapping =  {"bigleaguepolitics": bigleaguepolitics, "bizpacreview": bizpacreview, "breitbart": breitbart, "canadafreepress": canadafreepress, "chicksonright": chicksonright, "cnsnews": cnsnews, "conspiracydailyupdate": conspiracydailyupdate, "dailycaller": dailycaller, "dailywire": dailywire, "davidharrisjr": davidharrisjr, "en-volve": envolve, "gellerreport": gellerreport, "hotair": hotair, "legalinsurrection": legalinsurrection, "lifenews": lifenews, "lifezette": lifezette, "naturalnews": naturalnews, "newrightnetwork": newrightnetwork, "nworeport": nworeport, "palmerreport": palmerreport, "pjmedia": pjmedia, "rawstory": rawstory, "redstate": redstate, "rushlimbaugh": rushlimbaugh, "shareblue": shareblue, "theblaze": theblaze, "thefederalist": thefederalist, "thegatewaypundit": thegatewaypundit, "thepoliticalinsider": thepoliticalinsider, "therightscoop": therightscoop, "truepundit": truepundit, "twitchy": twitchy,"westernfreepress": westernfreepress, "wnd": wnd, "zerohedge": zerohedge}


        """ Fetch articles """

        idx=0
        articles = []
	
        while idx < len(all_data):
            if all_data[idx]['newssource'] == 'breitbart':
                soup = fromstring(all_data[idx]['htmltree'])
                newssource = all_data[idx]['newssource']
                print("Fetching article on index: " + str(idx))
                idx = idx+1
            else:
                soup = BeautifulSoup(all_data[idx]['htmltree'], 'html.parser')
                newssource = all_data[idx]['newssource']
                print("Fetching article on index: " + str(idx))
                idx = idx+1
            try:
                article = mapping.get(newssource, fallback)(soup)
                articles.append(article)
            except:
                article = fallback(soup)
                articles.append(article)
      
        for i in articles:
            i['title'] = u' '.join(i['title'].split())
            i['text'] = u' '.join(i['text'].split())

        result = [ {**d1, **d2} for d1, d2 in zip(all_data, articles) ]
        
        print("Returning a dictionary.")
        
        return result
