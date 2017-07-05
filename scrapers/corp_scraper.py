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

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()


# Dutch companies

class philips(rss):
    """Scrapes Philips """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "philips (corp)"
        self.rss_url ='http://www.lighting.philips.com/main/company/newsroom/n13-newscenter-archive-browser.feeds.xml'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*/span[@class="p-heading-02 p-heading-medium"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            teaser="".join(tree.xpath('//*/span[@class="p-body-copy-02"]/text()')).strip()
 #           print("this prints teaser dirty", teaser)
        except:
            print("no teaser")
            teaser= ""
        teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*/span[@class="p-body-copy-02"]//text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser_clean.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class boskalispress (rss):
    """Scrapes Boskalis Westminster Press Releases"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "boskalis press (corp)"
        self.rss_url ='https://boskalis.com/syndication/press-releases/feed.rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*/h1[@class="heading--section"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*/a[@class="btn btn--link"]//text()')).strip()
#            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text="".join(tree.xpath('//*[@class="page-content content--main"]//text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class boskalisnews (rss):
    """Scrapes Boskalis Westminster News Releases"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "boskalis news (corp)"
        self.rss_url ='https://boskalis.com/syndication/news-releases/feed.rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*/h1[@class="heading--section"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*/span[@class="tag"]//text()')).strip()
#            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text="".join(tree.xpath('//*[@class="page-content content--main"]//text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class unilever (rss):
    """Scrapes Unilever"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "unilever (corp)"
        self.rss_url ='https://www.unilever.com/feeds/news.rss'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*/article[@class="content-article"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*[@class="small-12 end"]/ul/li/a/text()')).strip()
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
            text="".join(tree.xpath('//*/article[@class="content-article"]/section//text()')).strip()
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

class aegon (rss):
    """Scrapes Aegon"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "aegon (corp)"
        self.rss_url ='https://nieuws.aegon.nl/feed/nl.xml'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*[@class="title_companyprofile"]/h1//text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            teaser="".join(tree.xpath('//*[@class="text_summary"]/p//text()')).strip()
 #           print("this prints teaser dirty", teaser)
        except:
            print("no teaser")
            teaser= ""
        teaser_clean = " ".join(teaser.split())
        try:
            text="".join(tree.xpath('//*[@class="text_companyprofile"]/div/p//text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class ing (rss):
    """Scrapes ING"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "ing (corp)"
        self.rss_url ='https://www.ing.com/news.rss'
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
            title="".join(tree.xpath('//*/section[@class="article-main"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            teaser="".join(tree.xpath('//*[@class="article-intro"]/p//text()')).strip()
 #           print("this prints teaser dirty", teaser)
        except:
 #          print("no teaser")
            teaser= ""
        teaser_clean = " ".join(teaser.split())
        try:
            text=" ".join(tree.xpath('//*/section[@class="article-main"]/div/p//text()')).strip()
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

class asml (rss):
    """Scrapes ASML"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "asml (corp)"
        self.rss_url ='https://www.asml.com/asml/rss/pressreleases'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*[@class="section"]/h2/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            text="".join(tree.xpath('//*[@class="body"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class relx (rss):
    """Scrapes Relx"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "relx (corp)"
        self.rss_url ='http://www.relx.com/_layouts/feed.aspx?xsl=1&web=%2Fmediacentre&page=79e16d86-97d3-4f5c-bc80-73e834388924&wp=43d94ca0-83d8-4583-8b96-5b9b9152fc08&pageurl=%2Fmediacentre%2FPages%2FRSSFeed%2Easpx'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*/h1[@class="row"]/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            text="".join(tree.xpath('//*[@class="zone-full-width content-page-body-intro"]//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo

class abnamro (rss):
    """Scrapes ABN Amro"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "abnamro (corp)"
        self.rss_url ='https://www.abnamro.com/en/newsroom/rss.html'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=14)


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
            title="".join(tree.xpath('//*/article[@class="news-detail"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*/ul[@class="keywords"]/li/a/text()')).strip()
#            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text="".join(tree.xpath('//*[@class="articleBody"]/ul//text() | //*[@class="articleBody"]/p//text()')).strip()
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

class gemalto (rss):
    """Scrapes Gemalto"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "gemalto (corp)"
        self.rss_url ='http://www.gemalto.com/_layouts/15/feed.aspx?xsl=1&web=/press/rss&page=ccdbcfc3-cf39-419e-ad30-ff414b97b068&wp=9cc71aca-9378-474a-98a2-99673b290d2b'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)


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
            title="".join(tree.xpath('//*[@class="sub-content"]/h1/text()')).strip()
#            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            text="".join(tree.xpath('//*[@class="ms-rtestate-field"]//text() | //*[@class="articleBody"]/p//text()')).strip()
        except:
#          print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo


class shell(Scraper):
    """Scrapes Shell"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "http://www.shell.com/media/news-and-media-releases.html"
        self.BASE_URL = "http://www.shell.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Shell
        '''
        self.doctype = "shell (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)

        releases = [] #
        overview_page = requests.get(self.START_URL)
        tree = fromstring(overview_page.text)

        linkobjects = tree.xpath('//h3//a')

        links = [self.BASE_URL+l.attrib['href'] for l in linkobjects]

        for link in links: 
            logger.debug('ik ga nu {} ophalen'.format(link))
            current_page = requests.get(link)
            tree = fromstring(current_page.text)
            #tree.xpath('//*[@class="promo-list__list"]/article/div/div/h3/a//text()').strip() # parse interesting stuff from specific sites
            try:
                title=" ".join(tree.xpath('//*[@class="page-header__header"]/h1/text()'))
#                print("this prints title", title)
            except:
                print("no title")
                title = ""
            try:
                teaser=" ".join(tree.xpath('//*[@class="page-header__text"]/p//text()'))
 #               print("this prints teaser dirty", teaser)
            except:
 #              print("no teaser")
                teaser= ""
            teaser_clean = " ".join(teaser.split())
            try:
                text=" ".join(tree.xpath('//*[@class="text-image__text"]//text()'))
            except:
#           print("geen text")
                logger.info("oops - geen textrest?")
                text = ""
            text = "".join(text)
            releases.append({'text':text.strip(),
                             'teaser': teaser.strip(),
                             'title':title.strip(),
                             'url':link.strip()})

        return releases

class akzonobel(Scraper):
    """Scrapes Akzo Nobel"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.akzonobel.com/media-releases-and-features"
        self.BASE_URL = "http://www.akzonobel.com/"

    def get(self):
        '''                                                                             
        Fetches articles from Akzo Nobel
        '''
        self.doctype = "shell (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)

        releases = []
        overview_page = requests.get(self.START_URL)
        tree = fromstring(overview_page.text)

        linkobjects = tree.xpath('//h3//a')

        links = [self.BASE_URL+l.attrib['href'] for l in linkobjects]

        for link in links:
            logger.debug('ik ga nu {} ophalen'.format(link))
            current_page = requests.get(link)
            tree = fromstring(current_page.text)
            #tree.xpath('//*[@class="promo-list__list"]/article/div/div/h3/a//text()').strip() # parse interesting stuff from specific sites
            try:
                title=" ".join(tree.xpath('//*[@class="page-header__header"]/h1/text()'))
#                print("this prints title", title)
            except:
                print("no title")
                title = ""
            try:
                teaser=" ".join(tree.xpath('//*[@class="page-header__text"]/p//text()'))
 #               print("this prints teaser dirty", teaser)
            except:
 #              print("no teaser")
                teaser= ""
            teaser_clean = " ".join(teaser.split())
            try:
                text=" ".join(tree.xpath('//*[@class="text-image__text"]//text()'))
            except:
#           print("geen text")
                logger.info("oops - geen textrest?")
                text = ""
            text = "".join(text)
            releases.append({'text':text.strip(),
                             'teaser': teaser.strip(),
                             'title':title.strip(),
                             'url':link.strip()})

        return releases


# UK Companies

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
    """Scrapes Diageo Press Releases"""

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
            text="".join(tree.xpath('//*[@class="text-container"]/p//text()')).strip()
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
            text="".join(tree.xpath('//*[@class="cb"]//text() | //*[@class="ca"]//text() | //*[@class="cg"]//text()')).strip()
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