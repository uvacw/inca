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

class dailymail(rss):
    """Scrapes dailymail.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "dailymail (www)"
        self.rss_url='http://www.dailymail.co.uk/articles.rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=8, day=30)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")

#category
#category
        try:
            category = r[0]['url'].split('/')[3]
        except:
            category = ""       

#teaser: The articles on daily mail do not have teasers.

#title
        try:
            title = tree.xpath('//*[@itemscope="itemscope"]//h1//text()')[0]
        except:
            title =""
#text
        try:
            text = ''.join(tree.xpath('//*[@itemprop="articleBody"]/p//text()')).replace('\xa0','')
        except:
            text = ''
#author
        try:
            author = ''.join(tree.xpath('//*[@class="author"]//text()')).split(' ',6)[:2]
        except:
            author = ''
            
#source
        extractedinfo={'category':category,
                       'title':title,
                       'text':text,
                       'byline':author
                       }
        
        return extractedinfo
