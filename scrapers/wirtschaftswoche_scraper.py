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

class wirtschaftswoche(rss):
    """Scrapes wiwo.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "wiwo (www)"
        self.rss_url='http://www.wiwo.de/contentexport/feed/rss/schlagzeilen'
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
            category ="" 
        except:
            category=""
#teaser
        try:
            teaser = tree.xpath('//*[@class="hcf-teaser"]//text()')
        except:
            teaser = ""


#text: werkt nog niet
        try:
            text = tree.xpath('//*[@itemprop="aticleBody"]//text()')
        except:
            text = ""

#author: werkt nog niet
        try:
            author = tree.xpath('//*[@class="hcf-author"]//text()')[1]
        except:
            author =""
            
#source:
        try:
            source = tree.xpath('//*[@class="hcf-gallery-caption"]//a/text()')
        except:
            source = ""

#title: title is written in two parts. this path gets both with a ':' in the middle.

        try:
            title = "".join(tree.xpath('//*[@class="hcf-colset1"]//h2//text()'))
        except:
            title = ""



        extractedinfo={"category":category.strip(),
                       "title":title,
                       "byline_source":source,
                       "text":text,
                       "teaser":teaser,
                       "byline":author
                       }

        return extractedinfo
