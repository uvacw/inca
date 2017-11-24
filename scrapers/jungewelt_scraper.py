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

class jungewelt(rss):
    """Scrapes jungewelt.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "jungewelt (www)"
        self.rss_url='https://www.jungewelt.de/feeds/newsticker.rss'
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
        
#title
        try:
            title = tree.xpath('//*[@class="Article"]//h1/text()')
        except:
            title =""

#category: this newssite has strange categeories:
        try:
            category = tree.xpath('//*[@class="Date"]//text()')[3].split('/',1)[1]
        except:
            category =""
#author
        try:
            author = tree.xpath('//*[@class="Article"]//address/text()')[0].replace("Von","").strip()

        except:
            author =""
#source
        try:
            source = tree.xpath('//*[@class="Content"]//text()')[-1].split(" ",100)[-1].replace("("," ").replace(")"," ").replace("/"," ")
        except:
            source =""
#teaser
        try:
            teaser = tree.xpath('//*[@class="Article"]//h2/text()')[0].replace("Von","").strip()
        except:
            teaser =""
#text
        try:
            text = "".join(tree.xpath('//*[@class="Content"]//text()')).strip().replace("\n","")
        except:
            text =""

        extractedinfo={"title":title,
                       "byline":author,
                       "text":text,
                       "teaser":teaser,
                       "category":category,
                       "byline_source":source
                       }

        return extractedinfo
