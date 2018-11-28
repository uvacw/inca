from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import parse
import datetime
from ..core.scraper_class import Scraper
import time
import requests

scraper = Scraper()

class junknews_scraper(Scraper):

    def __init__(self):

        self.doctype = "junknews_scraper"
        self.START_URL = "https://newsaggregator.oii.ox.ac.uk/news/app/"
        self.version = ".1"
        self.datetime = datetime.datetime(year=2018, month=11, day=28)

    def get(self, save, *args, **kwargs):

        """Gets junk news articles from Oxford Internet Institute's Junk News Aggregator"""
        
        """ Find publishers, websites and facebooksites  """

        driver = webdriver.Firefox()
        driver.get(self.START_URL)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@value="3"]').click() #3, can also be changed to 6
        time.sleep(5)

        x = driver.find_elements_by_xpath('//a[@class="link-website"]') # Websites
        fb = driver.find_elements_by_xpath('//a[@class="link-facebook"]') # FBsites
        y = driver.find_elements_by_xpath('//span[@class="publisher"]') # Publishers

        publishers = []
        for i in y:
            publishers.append(i.text) 

        websites = []
        for i in x: 
            websites.append(str(i.get_attribute("href")))

        facebooksites = []
        for i in fb: 
            facebooksites.append(str(i.get_attribute("href")))


        """ Get newssources and htmltrees, combine lists into a dict """
   

        def getnewssource(webpage):
            newssource = parse.urlsplit(webpage).netloc
            if newssource.startswith("www."):
                newssource = newssource[4:]
            sep = '.'
            newssource = newssource.split(sep, 1)[0]
            return newssource
 
        def gettree_chicks(webpage):
            driver = webdriver.Firefox()
            driver.get(webpage)
            time.sleep(15)
            try:
                driver.find_element_by_xpath('//button[@class="button_button intro_acceptAll "]').click()
            except:
                print("No button.")
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
        for a in websites:
            newssources.append(getnewssource(a))

        trees_data = []
        for i in websites:
            trees_data.append(gettree(i))

        all_data = [{'website': w, 'publisher': p, 'newssource': n, 'facebooksite': f, 'htmltree': t} for w, p, n, f, t in zip(websites, publishers, newssources, facebooksites, trees_data)]

    
        """ General function for extracting article text """


        def getarticle(s, chunck, element, name):
            article = s.find(chunck, {element : name}).findAll('p')
            entrycontent = ""
            for element in article:
                entrycontent += '\n' + ' '.join(element.findAll(text = True))
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
            return(title, entrycontent, "bigleaguepolitics")

        def bizpacreview(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            sep = "We know first-hand that censorship against conservative news is real"
            entrycontent = entrycontent.split(sep, 1)[0]
            return(title, entrycontent, "bizpacreview")

        def breitbart(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return(title, entrycontent, "breitbart")
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
            return(title, entrycontent, "canadafreepress")

        def chicksonright(soup):
            title = soup.h1.text
            tweets = soup.find_all('p', {'class': 'Tweet-text e-entry-title'})
            entrycontent = getarticle(soup, "div", "class", "td-post-content")
            entrycontent = entrycontent.replace('Email address','')
            return(title, entrycontent, "chicksonright")
 
        """ Chicksonright is the only function that does not retain twitter-
            blockquotes (because HTML scraped with the help of selenium). So we
            could try to fix "chicksonright" and keep the Twitter-content? """
    
        def cnsnews(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "field-items")
            return(title, entrycontent, "cnsnews")

        def conspiracydailyupdate(soup): 
            title = soup.find("h1", {"class":  "entry-title"}).text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return(title, entrycontent, "conspiracydailyupdate")
        """ Note! Most often no text, just links to other websites """

        def dailycaller(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "id", "ob-read-more-selector")
            sep = "Content created by The Daily Caller News Foundation is available without charge"
            entrycontent = entrycontent.split(sep, 1)[0]
            return(title, entrycontent, "dailycaller")

        def dailywire(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "field-body")
            return(title, entrycontent, "dailywire")

        def davidharrisjr(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "vw-post-content clearfix")
            sep = 'To stay up to date with David’s No Nonsense News'
            entrycontent = entrycontent.split(sep, 1)[0]
            return(title, entrycontent, "davidharrisjr")

        def envolve(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "itemprop", "articleBody")
            return(title, entrycontent, "envolve")

        def gellerreport(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            sep = "Your contribution supports independent journalism"
            entrycontent = entrycontent.split(sep, 1)[0]
            return(title, entrycontent, "gellerreport")

        def hotair(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "col-xs-12 article-text")
            return(title, entrycontent, "hotair")

        def legalinsurrection(soup):
            title = soup.find("h2", {"class":  "postTitle"}).text
            entrycontent = getarticle(soup, "div", "class", "postContent")
            return(title, entrycontent, "legalinsurrection")

        def lifenews(soup):
            title = soup.h2.text
            entrycontent = getarticle(soup, "div", "class", "article")
            entrycontent = entrycontent.replace('ADVERTISEMENT','')
            return(title, entrycontent, "lifenews")

        def lifezette(soup):
            title = soup.h1.text
            subtitle = soup.h2.text
            soup = soup.find("div", {"class":"text font-default font-size-med"})
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = subtitle + soup.get_text()
            entrycontent = entrycontent.replace('Advertisement','')
            return(title, entrycontent, "lifezette")
        """ Contains: "advertisement", "Related: " """

        def naturalnews(soup):
            title = soup.find("h1", {"class":  "entry-title"}).text
            entrycontent = soup.find("div", {"class":  "entry-content"}).text
            return(title, entrycontent, "naturalnews")

        def newrightnetwork(soup):
            title = soup.h1.text
            entrycontent = soup.find("div", {"class":  "mtl-post-content"}).text
            return(title, entrycontent, "newrightnetwork")

        def nworeport(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "post-content")
            return(title, entrycontent, "nworeport")

        def palmerreport(soup):
            title = soup.h1.text
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = getarticle(soup, "div", "class", "fl-post-content clearfix")
            return(title, entrycontent, "palmerreport")

        def pjmedia(soup):
            title = soup.h3.text
            entrycontent = getarticle(soup, "div", "class", "pages")
            return(title, entrycontent, "pjmedia")
        """ Note: the second part of very long articles is dynamically loaded,
            so can't be accessed. Should I write an additional HTML-scraper to it? """
    
        def rawstory(soup):
            title = soup.find("h1", {"class":  "blog-title"}).text
            entrycontent = getarticle(soup, "div", "class", "blog-content https-content")
            return(title, entrycontent, "rawstory")

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
            return(title, entrycontent, "redstate")

        def rushlimbaugh(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return(title, entrycontent, "rushlimbaugh")
    
        def shareblue(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "td-post-content")
            return(title, entrycontent, "shareblue")

        def theblaze(soup):
            title = soup.h1.text
            entrycontent = soup.find("div", {"class": "entry-content"}).text
            return(title, entrycontent, "theblaze")
        """ Some of the extracted sentences seem to not be space-delimited """

        def thefederalist(soup): 
            title = soup.h2.text
            subtitle = soup.find("div", {"class": "subtitle"}).text
            entrycontent = subtitle
            for element in soup.select("div[class*=entry-content]"):
                entrycontent += '\n' + ' '.join(element.findAll(text = True))
            return(title, entrycontent, "thefederalist")

        def thegatewaypundit(soup):
            title = soup.h2.text
            #subtitle = soup.h3.text # Only sometimes present: needs an if-clause.
            entrycontent = getarticle(soup, "div", "class", "clearfix")
            sep = "As a privately owned web site"
            entrycontent = entrycontent.split(sep, 1)[0]
            return(title, entrycontent, "thegatewaypundit")

        def thepoliticalinsider(soup):
            title = soup.find("header", {"class":  "article-header row"}).text
            entrycontent = soup.find("div", {"id": "article-body"}).text
            return(title, entrycontent, "thepoliticalinsider")
 
        def therightscoop(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            return(title, entrycontent, "therightscoop")

        def truepundit(soup):
            title = soup.h1.text
            entrycontent = getarticle(soup, "div", "itemprop", "articleBody")
            return(title, entrycontent, "truepundit")

        def twitchy(soup):
            title = soup.h1.text
            soup = soup.find("div", {"class":"col-xs-9 article-text"})
            for item in soup.findAll("div", {"class":"home-trending-widget-article"}):
                item.extract() # Trending-widget: not in all, but in some articles
            for script in soup(["script", "style"]):
                script.extract()
            entrycontent = soup.get_text()
            sep = "Share on Facebook\n"
            entrycontent = entrycontent.split(sep, 1)[0] 
            return(title, entrycontent, "twitchy")

        def westernfreepress(soup):
            title = soup.h1.text
            soup.find('ul', class_="essb_links_list").decompose()
            entrycontent = getarticle(soup, "div", "class", "entry-content")
            if len(entrycontent) > 0:
                return(title, entrycontent, "westernfreepress")
            else:
                fallback(soup)
        """ Important: does fallback automatically return its output, or does westernfreepress
            have to take fallback's output, and return it? """

        def wnd(soup):
            title = soup.h1.text
            try:
                entrycontent = getarticle(soup, "div", "class", "entry-content wnd")
                return(title, entrycontent, "wnd")
            except:
                entrycontent = getarticle(soup, "div", "class", "entry-content non-wnd")
                return(title, entrycontent, "wnd")

        def zerohedge(soup):
            title = soup.find("h1", {"class": "page-title"}).text
            entrycontent = getarticle(soup, "div", "class", "node__content")
            return(title, entrycontent, "zerohedge")

        def fallback(soup):
            print("Fallback-method.")
            title = "NaN"
            for script in soup (["script", "style"]):
                script.extract()
            entrycontent = soup.get_text()
            lines = (line.strip() for line in entrycontent.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            entrycontent = '\n'.join(chunk for chunk in chunks if chunk)
            return(title, entrycontent, "fallback")

 
        """ Mapping functions to newssources """
 

        mapping =  {"bigleaguepolitics": bigleaguepolitics, "bizpacreview": bizpacreview, "breitbart": breitbart, "canadafreepress": canadafreepress, "chicksonright": chicksonright, "cnsnews": cnsnews, "conspiracydailyupdate": conspiracydailyupdate, "dailycaller": dailycaller, "dailywire": dailywire, "davidharrisjr": davidharrisjr, "en-volve": envolve, "gellerreport": gellerreport, "hotair": hotair, "legalinsurrection": legalinsurrection, "lifenews": lifenews, "lifezette": lifezette, "naturalnews": naturalnews, "newrightnetwork": newrightnetwork, "nworeport": nworeport, "palmerreport": palmerreport, "pjmedia": pjmedia, "rawstory": rawstory, "redstate": redstate, "rushlimbaugh": rushlimbaugh, "shareblue": shareblue, "theblaze": theblaze, "thefederalist": thefederalist, "thegatewaypundit": thegatewaypundit, "thepoliticalinsider": thepoliticalinsider, "therightscoop": therightscoop, "truepundit": truepundit, "twitchy": twitchy,"westernfreepress": westernfreepress, "wnd": wnd, "zerohedge": zerohedge}


        """ Fetch articles """

        idx=0
        content = []
        while idx < len(all_data):
            soup = BeautifulSoup(all_data[idx]['htmltree'], 'html.parser')
            newssource = all_data[idx]['newssource']
            print("Fetching article on index: " + str(idx))
            idx = idx+1
            try:
                contents = mapping.get(newssource, fallback)(soup)
                content.append(contents)
            except:
                contents = fallback(soup)
                content.append(contents)

        content = [{"1. Title": a, "2. Entrycontent": b, "3. Function": c} for a,b,c in content]
      
        for i in content:
            i['1. Title'] = u' '.join(i['1. Title'].split())
            i['2. Entrycontent'] = u' '.join(i['2. Entrycontent'].split())

        result = [ {**d1, **d2} for d1, d2 in zip(all_data, content) ]
        
        print("Returning a dictionary.")
        
        return result
