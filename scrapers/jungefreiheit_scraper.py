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

class jungefreiheit(rss):
    """Scrapes jungefreiheit.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "jungefreiheit (www)"
        self.rss_url='https://jungefreiheit.de/feed/'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=7, day=1)

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
        try:
            category = tree.xpath('//*[@class="breadcrumb"]//span/text()')[0]
        except:
            category = ""
 #title1
        try:
            title1 = ' '.join(tree.xpath('//*[@class="entry-header"]/div/a/text()')).strip()
        except:
            title1 = ""
#title2
        try:
            title2 = ' '.join(tree.xpath('//*[@class="entry-title"]//text()')).strip()
        except:
            title2 = ""
            
        title = title1 + '\n ' + title2
        
 #author:
        try:
            author = tree.xpath('//*[@class="entry-header"]/p//span/text()')
        except:
            author = ""
            
#teaser: teaser is not on the same webpage as the article. it can only be seen before selecting the article: Therefore no teaser being scraped.

 #text: doesnt work
        try:
            text = "".join(tree.xpath('//*[@itemprop="text"]/p/text()'))
        except:
            text =""
 
        extractedinfo={"category":category,
                       "byline":author,
                       "text":text,
                       "title": title
                       }

        return extractedinfo
