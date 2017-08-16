import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

from scrapers.corp_abnamro import *
from scrapers.corp_aegon import *
from scrapers.corp_akzonobel import *
from scrapers.corp_asml import *
from scrapers.corp_barclays import *
from scrapers.corp_boskalis import *
from scrapers.corp_bsch import *
from scrapers.corp_dsm import *
from scrapers.corp_gemalto import *
from scrapers.corp_ing import *
from scrapers.corp_kpn import *
from scrapers.corp_lbg import *
from scrapers.corp_philips import *
from scrapers.corp_sbm import *
from scrapers.corp_shell import *
from scrapers.corp_unilever import *
from scrapers.corp_vopak import *
from scrapers.corp_wolters import *

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

# Dutch companies

class randstad(Scraper):
    """Scrapes Randstad Holdings"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.ir.randstad.com/news-and-events/press-releases.aspx"
        self.BASE_URL = "https://www.ir.randstad.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Randstad Holdings
        '''
        self.doctype = "Randstad (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

        releases = []

        page = 1
        overview_page = requests.get(self.START_URL+'?page='+str(page))
        tree = fromstring(overview_page.text)
        overview_page_text = tree.xpath('//*[@class="textContainer"]')

        first_page_text = ''
        while overview_page_text != first_page_text:

            if page == 1:
                first_page_text = tree.xpath('//*[@class="textContainer"]')
    
            linkobjects = tree.xpath('//*[@class="press-title"]//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="pr-Title"]/h2/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="pr-Content"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?page='+str(page)
            overview_page = requests.get(current_url)
            tree = fromstring(overview_page.text)
            overview_page_text = tree.xpath('//*[@class="textContainer"]')

        return releases

# UK Companies

class abf(Scraper):
    """Scrapes Associated British Foods"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.abf.co.uk/media/news"
        self.BASE_URL = "https://www.abf.co.uk"

    def get(self):
        '''                                                                             
        Fetches articles from Associated British Foods
        '''
        self.doctype = "ABF (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=28)

        releases = []

        current_url = self.START_URL
        start_page = requests.get(current_url)
        tree = fromstring(start_page.text)
        yearobjects = tree.xpath('//*/ul[@class="tab-header"]//a')
        years = [self.BASE_URL+l.attrib['href'] for l in yearobjects if 'href' in l.attrib]
        
        for year in years:

            current_url = year
            year_page = requests.get(current_url)
            tree = fromstring(year_page.text)
    
            linkobjects = tree.xpath('//*[@class="annual-details"]//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            print(links)
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="content-main"]/h1/text()'))
        #            print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class="content-main"]/h4//text()'))
         #           print("this prints teaser dirty", teaser)
                except:
         #          print("no teaser")
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="content-main"]/p//text() | //*[@class="content-main"]/h3//text() | //*[@class="content-main"]/ul//text()'))
                except:
        #       print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'teaser':teaser.strip(),
                                 'url':link.strip()})
        return releases



class bat(Scraper):
    """Scrapes British American Tobacco"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.bat.com/group/sites/UK__9D9KCY.nsf/vwPagesWebLive/DO6YLKYF"
        self.BASE_URL = "http://www.bat.com"

    def get(self):
        '''                                                                             
        Fetches articles from British American Tobacco
        '''
        self.doctype = "BAT (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=26)

        releases = []

        current_url = self.START_URL
        start_page = requests.get(current_url)
        tree = fromstring(start_page.text)
        yearobjects = tree.xpath('//*/ul[@class="ow_tabnav_ul"]//a')
        years = [self.BASE_URL+l.attrib['href'] for l in yearobjects if 'href' in l.attrib]
        
        for year in years:

            current_url = year
            year_page = requests.get(current_url)
            tree = fromstring(year_page.text)
    
            linkobjects = tree.xpath('//*[@class="stackRow"]//a[@class="link"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="title"]/p/text()'))
    #                print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="primaryContent gutterTop"]//text()'))
                except:
    #           print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})#

        return releases

class bhp(Scraper):
    """Scrapes BHP Billiton"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.bhp.com/media-and-insights/news-releases"
        self.BASE_URL = "http://www.bhp.com/"

    def get(self):
        '''                                                                             
        Fetches articles from BHP Billiton
        '''
        self.doctype = "BHP (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=26)

        releases = []

        page = 0
        current_url = self.START_URL+'?q0='+str(page)
        overview_page = requests.get(current_url)
        while overview_page.text.find('listing__item-wrap') != -1:
            
            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*[@class="col-9"]/h2//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="col-9 col-r"]/h2/text()'))
        #            print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="rte col-12"]//text()'))
                except:
        #       print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?q0='+str(page)
            overview_page = requests.get(current_url)

        return releases

class bp(Scraper):
    """Scrapes BP"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.bp.com/en/global/corporate/media/press-releases.html"
        self.BASE_URL = "http://www.bp.com/"

    def get(self):
        '''                                                                             
        Fetches articles from BP
        '''
        self.doctype = "BP (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

        releases = []

        page = 1
        current_url = self.START_URL+'?page='+str(page)
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'Sorry, nothing found') == -1:
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*/ul[@class="list"]/li//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*/h1[@class="nv-page-title"]/text()'))
    #                print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class="nv-richtext"]/h2//text()'))
     #               print("this prints teaser dirty", teaser)
                except:
     #              print("no teaser")
                    teaser= ""
                teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="nv-richtext"]/p//text() | //*[@class="nv-parsys-component nv-container"]//text()'))
                except:
    #           print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'teaser': teaser.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?page='+str(page)
            overview_page = requests.get(current_url)

        return releases

class btgroup (rss):
    """Scrapes BTGroup"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "btgroup (corp)"
        self.rss_url ='http://bt.mynewsdesk.com/rss/source/56578/pressrelease'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h1[@class="newsroom-headline fn"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            text="".join(tree.xpath('//*[@class="clearfix"]//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class compass(Scraper):
    """Scrapes Compass Group"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.compass-group.com/en/media/news.html"
        self.BASE_URL = "https://www.compass-group.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Compass Group
        '''
        self.doctype = "Compass (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=26)

        releases = []

        year = 2012
        current_url = self.START_URL+'?tab1='+str(year)
        overview_page = requests.get(current_url)
        while overview_page.text.find('list-item list-item-even') != -1:
            
            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*/p[@class="article-list-item-date"]//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="default"]/h2/text()'))
        #            print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    text=" ".join(tree.xpath('//*[@class="default"]/p//text()'))
                except:
        #       print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            year+=1
            current_url = self.START_URL+'?tab1='+str(year)
            overview_page = requests.get(current_url)

        return releases

class diageopress(rss):
    """Scrapes Diageo Press Releases"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "diageo (corp)"
        self.rss_url ='https://www.diageo.com/en/rss/press-releases/'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-0"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*/p[@class="intro large"]//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="text-container"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class diageonews(rss):
    """Scrapes Diageo News"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "diageo (corp)"
        self.rss_url ='https://www.diageo.com/en/rss/all-news-and-media/'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-2"]/h1/text() | //*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-2"]/h1/text() | //*[@class="col-xs-12 col-md-10 col-md-offset-1 col-lg-8 col-lg-offset-0"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            category="".join(tree.xpath('//*//[@class="badge feature"]//text()')).strip()
#            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            teaser="".join(tree.xpath('//*/p[@class="intro large"]//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="text-container"]//text() | //*/p[@class="u-top-padding-half"]//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class gsk(Scraper):
    """Scrapes GlaxoSmithKline"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.gsk.com/en-gb/media/press-releases/"
        self.BASE_URL = "http://www.gsk.com/"

    def get(self):
        '''                                                                             
        Fetches articles from GSK
        '''
        self.doctype = "GSK (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

        releases = []

        page = 1
        current_url = self.START_URL+'/?p='+str(page)
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'Sorry, there are no search results.') == -1:
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*[@class="simple-listing__link"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="content-wrapper"]/h1/text()'))
    #                print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class="intro"]/p//text()'))
     #               print("this prints teaser dirty", teaser)
                except:
     #              print("no teaser")
                    teaser= ""
                teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="content-wrapper"]/p//text()'))
                except:
    #           print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'teaser': teaser.strip(),
                                 'title':title.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'/?p='+str(page)
            overview_page = requests.get(current_url)

        return releases



class prudential(rss):
    """Scrapes Prudential"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "diageo (corp)"
        self.rss_url ='http://news.prudential.com/rss.xml'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@id="articleDateTitle"]/h2/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            category="".join(tree.xpath('//*[@id="articleTags"]/p/a/text()')).strip()
#            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text="".join(tree.xpath('//*[@id="articleContent"]//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class riotinto(rss):
    """Scrapes Rio Tinto"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "riotinto (corp)"
        self.rss_url ='http://coapi.riotinto.com/rss/130'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/header[@class="responsive mobile-only"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            text="".join(tree.xpath('//*[@class="body-text"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class glencore(rss):
    """Scrapes Glencore"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "glencore (corp)"
        self.rss_url ='http://www.glencore.com/media/news/rss/%20'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="typography"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            text="".join(tree.xpath('//*[@class="typography"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class nationalgrid(rss):
    """Scrapes National Grid"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "nationalgrid (corp)"
        self.rss_url ='http://media.nationalgrid.com/rss/'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="text"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*[@class="text"]/p/text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="panel-body"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class rbs(rss):
    """Scrapes Royal Bank of Scotland"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "rbs (corp)"
        self.rss_url ='http://www.rbs.com/rss/news.rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h1[@class="title-heading"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*[@class="component-content metadata-description"]/p//text()')).strip()
#            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            teaser="".join(tree.xpath('//*[@class="intro"]/p/text()')).strip()
 #           print("this prints teaser dirty", teaser)
        except:
            print("no teaser")
            teaser= ""
        teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="component-content"]//text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class shire(rss):
    """Scrapes Shire"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "shire (corp)"
        self.rss_url ='https://www.shire.com/feeds/press-releases'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/span[@id="content_1_rowcontainer_1_pagecontentleftprimary_0_Heading"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            text="".join(tree.xpath('//*[@class="content-primary"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo


class standardchartered(rss):
    """Scrapes Standard Chartered"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "standardchartered (corp)"
        self.rss_url ='https://apps.standardchartered.com/RSSGenerator/RSS'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h1[@class="news_title"]/text()"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            text="".join(tree.xpath('//*[@class="content cols2-1"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class vodafone(Scraper):
    """Scrapes Vodafone"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.vodafone.com/content/index/media/vodafone-group-releases.html"
        self.BASE_URL = "http://www.vodafone.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Vodafone
        '''
        self.doctype = "Vodafone (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=24)

        releases = []

        page = 0
        current_url = self.START_URL+'?category=all&offset='+str(page)+'0'
        overview_page = requests.get(current_url)
        while overview_page.text.find('search-results-list') != -1:
            
            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*[@class="col lrg-50"]/h3//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*[@class="belt  "]/h1/text() | //*[@class="belt no-img "]/h1/text()'))
        #            print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class="article-blockquote"]/blockquote/p//text()'))
         #           print("this prints teaser dirty", teaser)
                except:
         #          print("no teaser")
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="richtexteditor section"]/p//text()'))
                except:
        #       print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'teaser':teaser.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'?category=all&offset='+str(page)+'0'
            overview_page = requests.get(current_url)

        return releases

# Spanish Companies

class iag(rss):
    """IAG"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "iag (corp)"
        self.rss_url ='http://www.iairgroup.com/corporate.rss?c=240949&Rule=Cat=news~subcat=ALL'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/span[@class="ccbnTtl"]//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            text="".join(tree.xpath('//*[@class="cb"]//text() | //*[@class="ca"]//text() | //*[@class="cg"]//text() | //*[@class="cc"]//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class telefonica(rss):
    """Telefonica"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "telefonica (corp)"
        self.rss_url ='https://www.telefonica.com/web/sala-de-prensa/rss/-/asset_publisher/RBb25zTLKrHp/rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=5)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h1[@class="header-title"]//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*[@class="journal-content-article"]/ul//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="journal-content-article"]/p//text() | //*[@class="ca"]//text() | //*[@class="cg"]//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class bbva(rss):
    """BBVA"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "BBVA (corp)"
        self.rss_url ='https://www.bbva.com/en/rss/press-releases'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=5)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h1[@class="titular"]//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*[@class="entradilla"]//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="container"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo 

class bpe(rss):
    """Banco Popular Espanol"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "BPE (corp)"
        self.rss_url ='https://www.comunicacionbancopopular.es/feed/?post_type=nota'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h3[@class="entry-title single-title"]/h3//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*[@class="entry-content clearfix"]/strong//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="entry-content clearfix"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo 

class abertis(rss):
    """abertis"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "Abertis (corp)"
        self.rss_url ='https://www.abertis.com/en/rss-news'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=5)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="col-sm-12 col-md-8"]/h2//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            text="".join(tree.xpath('//*[@class="news-text"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo  

class endesa(Scraper):
    """Scrapes Endesa"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.endesa.com/en/press/the-news.html"
        self.BASE_URL = "https://www.endesa.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Endesa
        '''
        self.doctype = "Endesa (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)

        releases = []

        page = 0
        current_url = self.START_URL+'#/page_'+str(page)
        overview_page = requests.get(current_url)
        first_page_text = ''
        while overview_page.text != first_page_text:

            if page == 0:
                first_page_text = overview_page.text
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*/h3[@class="list-item_title text--list-title-large"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title=" ".join(tree.xpath('//*/h1[@class="hero_title text--page-heading"]/text()'))
    #                print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    teaser="".join(tree.xpath('//*[@class="rich-text_inner"]/ul/li//text()')).strip()
    #           print("this prints teaser dirty", teaser)
                except:
    #           print("no teaser")
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())              
                try:
                    text=" ".join(tree.xpath('//*[@class="rich-text_inner"]/p//text()'))
                except:
    #           print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'teaser':teaser.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+'#/page_'+str(page)
            overview_page = requests.get(current_url)

        return releases

class gnf(rss):
    """Gas Natural Fenosa"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "GNF (corp)"
        self.rss_url ='http://prensagnf.azurewebsites.net/feed/'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=5)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/h2[@class="entry-title"]/a//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*[@class="post-content"]/ul//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="post-content"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo   

class mapfre(Scraper):
    """Scrapes Mapfre"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://noticias.mapfre.com/en/category/news-corporate/page/"
        self.BASE_URL = "https://noticias.mapfre.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Mapfre
        '''
        self.doctype = "Mapfre (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)

        releases = []

        page = 1
        current_url = self.START_URL+str(page)+'/'
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'Oops, This Page Could Not Be Found!') == -1:
            
            tree = fromstring(overview_page.text)
    
            linkobjects = tree.xpath('//*/h2[@class="entry-title fusion-post-title"]//a')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                #tree.xpath('//*[@class="promo-list__list"]/article/div/div/h3/a//text()').strip() # parse interesting stuff from specific sites
                try:
                    title=" ".join(tree.xpath('//*/h2[@class="entry-title fusion-post-title"]/text()'))
    #                print("this prints title", title)
                except:
                    print("no title")
                    title = ""
                try:
                    teaser="".join(tree.xpath('//*[@class="post-content"]/p/strong//text()')).strip()
 #                  print("this prints teaser dirty", teaser)
                except:
 #              print("no teaser")
                    teaser= ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text=" ".join(tree.xpath('//*[@class="post-content"]/p//text()'))
                except:
    #           print("geen text")
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append({'text':text.strip(),
                                 'title':title.strip(),
                                 'teaser':teaser.strip(),
                                 'url':link.strip()})

            page+=1
            current_url = self.START_URL+str(page)+'/'
            overview_page = requests.get(current_url)

        return releases

class ree(rss):
    """Gas Natural Fenosa"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "Red Electrica Corp (corp)"
        self.rss_url ='http://www.ree.es/en/feed/press_release/all'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=7, day=5)


    def parsehtml(self,htmlsource):
        '''                                                                             
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="field-item even"]/h2//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
        try:
            teaser="".join(tree.xpath('//*[@class="field-item even"]/ul//text()')).strip()
 #          print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
            teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="field-item even"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo            