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

class focus(rss):
    """Scrapes focus.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "ad (www)"
        self.rss_url='http://rss.focus.de/fol/XML/rss_folnews.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
            category = r[0]['url'].split('/')[3]
        except:
            category=""
            
#title
        try:
            title = tree.xpath('//h1//text()')

        except:
            title = ""

#author: only such a little amount of articles have an author it gets irrelavant for this webside
        author = ""

#teaser
        try:
            teaser ="".join(tree.xpath('//*[@class="leadIn"]//text()'))
        except:
            teaser =""

#text
        try:
            text ="".join(tree.xpath('//*[@class="textBlock"]//text()'))
        except:
            text = ""
#source
        try:
            source = tree.xpath('//*[@class="created"]//text()')
        except:
            source = ""

        extractedinfo={"category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline_source":source
                       }

        return extractedinfo
