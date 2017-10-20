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

class neuesdeutschland(rss):
    """Scrapes neues-deutschland.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "neuesdeutschland (www)"
        self.rss_url='https://www.neues-deutschland.de/rss/neues-deutschland.xml'
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
            category = tree.xpath('//*[@class="Active"]//text()')[0]
        except:
            category =""
#title
#title pt1:
        try:
            pt1 = tree.xpath('//*[@class="Article"]//text()')[10]
        except:
            pt1 =""
#title pt2:
        try:
            pt2 = tree.xpath('//*[@class="Article"]//text()')[12]
        except:
            pt2 =""
        title = pt1 + ":" + pt2
        
#teaser: cannot scrape the whole teaser, since only the first part is also on the article page
        try:
            teaser = tree.xpath('//article//h2/text()')
        except:
            teaser =""
#author
        try:
            author = tree.xpath('//*[@class="Author"]/text()')[0].replace("Von","")
        except:
            author =""
#source:
        try:
            source = tree.xpath('//*[@class="Main"]//i/text()')
        except:
            source =""
#text
        try:
            text = ''.join(tree.xpath('//*[@class="Content"]//p/text()')).strip()
        except:
            text =""


        extractedinfo={"title":title,
                       "byline":author,
                       "byline_source":source,
                       "text":text,
                       "category":category
                      }

        return extractedinfo
