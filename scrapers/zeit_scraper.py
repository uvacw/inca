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

class zeit(rss):
    """Scrapes zeit.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "zeit (www)"
        self.rss_url='http://newsfeed.zeit.de/all'
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
            title = tree.xpath('//*[@class="article-header"]//h1/span/text()')
        except:
            title =""
#category
        try:
            category = r[0]['url'].split("/")[3]
        except:
            category =""
#author
        try:
            author = tree.xpath('//*[@itemprop="author"]/a/span/text()')
        except:
            author =""
#source
        try:
            author = tree.xpath('//*[@class="metadata"]//span/text()')[0].replace("Quelle:","").strip()

        except:
            author =""
#teaser
        try:
            teaser = tree.xpath('//*[@class="summary"]//text()').strip()
        except:
            teaser =""
#text
        try:
            text = "".join(tree.xpath('//*[@class="paragraph article__item"]//text()')).strip().replace("\n","")

        except:
            text  =""
        

        extractedinfo={"title":title,
                       "category":category,
                       "teaser":teaser,
                       "byline":author,
                       "byline_source":source,
                       "text":text
                       }

        return extractedinfo
