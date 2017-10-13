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

class handelsblatt(rss):
    """Scrapes handelsblatt.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "handelsblatt (www)"
        self.rss_url=['http://www.handelsblatt.com/contentexport/feed/schlagzeilen','http://www.handelsblatt.com/contentexport/feed/wirtschaft','http://www.handelsblatt.com/contentexport/feed/top-themen','http://www.handelsblatt.com/contentexport/feed/finanzen','http://www.handelsblatt.com/contentexport/feed/marktberichte','http://www.handelsblatt.com/contentexport/feed/unternehmen','http://www.handelsblatt.com/contentexport/feed/politik','http://www.handelsblatt.com/contentexport/feed/technologie','http://www.handelsblatt.com/contentexport/feed/panorama','http://www.handelsblatt.com/contentexport/feed/sport','http://www.handelsblatt.com/contentexport/feed/hbfussball','http://www.handelsblatt.com/contentexport/feed/bildergalerien','http://www.handelsblatt.com/contentexport/feed/video']
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=8, day=2)

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
            category = tree.xpath('//*[@id="hcf-wrapper"]//span//text()')[1].replace('\xa0','')
        except:
            category =""
#teaser
        try:
            teaser = tree.xpath('//*[@itemprop="description"]//text()')
        except:
            teaser =""
#title
        try:
            title = tree.xpath('//*[@itemprop="headline"]//text()')[0].replace("\xa0"," ")
        except:
            title =""
#text
        try:
            text = "".join(tree.xpath('//*[@class="vhb-article-content"]//p//text()')[2::]).replace("\xa0"," ")
        except:
            text =""
#author
        try:
            author = tree.xpath('//*[@id="hcf-wrapper"]//*[@class="vhb-article-author-row"]//span/text()')
        except:
            author =""
#source
        try:
            source = tree.xpath('//*[@class="vhb-nav-link"]//text()')[0]
        except:
            source =""
            
        extractedinfo={"category":category,
                       "title":title,
                       "byline":author,
                       "byline_source":source,
                       "teaser":teaser,
                       "text":text
                       }
        
        return extractedinfo
