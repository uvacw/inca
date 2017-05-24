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

class standaard(rss):
    """Scrapes standaard.be"""
#rss feed different for all categories, only subcategories for nieuws so far included

    def __init__(self,database=True):
        self.database=database
        self.doctype = "standaard (www)"
        #self.rss_url=['http://www.standaard.be/rss/section/1f2838d4-99ea-49f0-9102-138784c7ea7c','http://www.standaard.be/rss/section/e70ccf13-a2f0-42b0-8bd3-e32d424a0aa0','http://www.standaard.be/rss/section/ab8d3fd8-bf2f-487a-818b-9ea546e9a859','http://www.standaard.be/rss/section/eb1a6433-ca3f-4a3b-ab48-a81a5fb8f6e2','http://www.standaard.be/rss/section/451c8e1e-f9e4-450e-aa1f-341eab6742cc','http://www.standaard.be/rss/section/8f693cea-dba8-46e4-8575-807d1dc2bcb7','http://www.standaard.be/rss/section/113a9a78-f65a-47a8-bd1c-b24483321d0f']
        self.rss_url='http://www.standaard.be/rss/section/1f2838d4-99ea-49f0-9102-138784c7ea7c'
        
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=5, day=3)

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
            category = tree.xpath('//ol/li[3]/a/b/text()')
        except:
            category=""            
# teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="article-full"]/*[@class="article__body"]/*[@class="intro"]//text()'))
        except:
            teaser =""
            
# text
        try:
            text = tree.xpath('//*[@class="article-full"]//*[@class="article__body"]/p/text()')
        except:
            text =""
            
# author
        try:
            author = tree.xpath('//*[@class="article__meta"]/p/a/text()')
        except:
            author =""
 
# bylinesource
# gives a list with either two or one entries: the first one is the date and if there is a second one it is the bylinesource
        try:
            sourceorganisation = tree.xpath('//*[@class="blend-in"]/text()')
            if len(sourceorganisation) == 2:
                source = sourceorganisation[-1]
            else:
                source  = ""
        except:
            sourceorganisation = ""


        extractedinfo = {"category":category,
                         "teaser":teaser.strip(),
                         "text":text,
                         "bylinesource":source,
                         "byline":author
                        }

        return extractedinfo
