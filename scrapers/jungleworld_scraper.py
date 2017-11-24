




































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

class jungleworld(rss):
    """Scrapes jungle.world.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "jungleworld (www)"
        self.rss_url=['https://jungle.world/rss.xml']
        
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=7, day=3)

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
# category
        try:
            category = tree.xpath('//*[@class="breadcrumb"]//li/a/text()')[-1]
        except:
            category = ""
# title

        try:
            title1 = ''.join(tree.xpath('//*[@class="field field-name-field-dachzeile"]//text()')).replace('\n','').strip()
        except:
            title1 = ""
        try:
            title2 = tree.xpath('//*[@class="page-title"]//text()')[0]
        except:
            title2 =""
        title = title1 + title2
# teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="lead"]//text()')).replace('\n','').strip()
        except:
            teaser =""
            
# text
        try:
            text = tree.xpath('//*[@class="ft"]/p/text()')
        except:
            text =""
            
# author
        try:
            author = tree.xpath('//*[@class="autor"]/a/text()')[0]
        except:
            author =""


        extractedinfo = {"category":category,
                         "teaser":teaser.strip(),
                         "byline":author,
                         "title":title.strip(),
                         "text":text
                        }

        return extractedinfo
