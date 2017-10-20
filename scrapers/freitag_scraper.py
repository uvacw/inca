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

class freitag(rss):
    """Scrapes freitag.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "freitag (www)"
        self.rss_url='https://www.freitag.de/@@RSS'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=22)

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
            category = tree.xpath('//*[@class="x-breadcrumbs"]//a/text()')[1].replace(' ','').replace('\n','')
        except:
            category = ""
#teaser
        try:
            teaser = tree.xpath('//*[@id="content"]/div/div/div/div//text()')[:3][-1].replace('\n','').strip()
        except:
            teaser = ""
#title
        try:
            title = ''.join(tree.xpath('//*[@class="row"]/h1/text()')[0].replace('\n','')).strip()
        except:
            title = ""
#text
        try:
            text = tree.xpath('//*[@class="Article"]//*[@class="Content"]/p/text()')
        except:
            text = ""
#author
        try:
            author = ''.join(tree.xpath('//*[@class="row"]//*[@class="author"]/a/text()')).replace('\n','').strip()
        except:
            author = ""

        extractedinfo={"category":category,
                       "title":title,
                       "text":text,
                       "byline":author,
                       "teaser":teaser
                       }
        
        return extractedinfo
