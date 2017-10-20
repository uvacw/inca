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

class diewelt(rss):
    """Scrapes welt.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "diewelt (www)"
        self.rss_url='https://www.welt.de/feeds/topnews.rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=7, day=2)

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
            category = tree.xpath('//*[@class="c-breadcrumb"]//a/span/text()')[1]
        except:
            category =""

#teaser
        try:
            teaser = tree.xpath('//*[@class="c-summary__intro"]//text()')
        except:
            teaser =""
#title1
        try:
            title1 = tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()')[1]
        except:
            title1 =""
#title2
        try:
            title2 = tree.xpath('//*[@class="c-dreifaltigkeit__headline-wrapper"]//text()')[3]
        except:
            title2 = ""
            
        title = title1 + title2
#text
        try:
            text = tree.xpath('//*[@data-content="Sticky.ArticleBody"]/div/p/span/text()')+''.join(tree.xpath('//*[@itemprop="articleBody"]/p/text()'))
        except:
            text =""
       
#author
        try:
            author = tree.xpath('//*[@class="c-author__name"]//text()')[1]
        except:
            author =""
#source
        try:
            source = tree.xpath('//*[@class="c-source"]//text()')
        except:
            source =""
            
        extractedinfo={"category":category,
                       "title":title,
                       "text":text,
                       "teaser":teaser,
                       "byline":author,
                       "byline_source":source
                       }
        
        return extractedinfo
