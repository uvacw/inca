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

class sueddeutsche(rss):
    """Scrapes sueddeutsche.de"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "ad (www)"
        self.rss_url='http://rss.sueddeutsche.de/app/service/rss/alles/index.rss?output=rss'
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
            category =""
#teaser
        try:
            teaser = "".join(tree.xpath('//*[@class="header"]//h2//text()')).replace("\n",'').strip()
        except:
            teaser =""
#title
        try:
            title = "".join(tree.xpath('//*[@class="header"]//h2//text()')).replace("\n",'').strip()
        except:
            title =""
#text
        try:
            text = "".join(tree.xpath('//*[@id="article-body"]//p/text()')).replace('Artikel',"").replace('\xa0',' ')
        except:
            text =""
#author
        try:
            author = tree.xpath('//*[@class="authorContainer"]//text()')[8]
        except:
            author =""
#source
        try:
            source = tree.xpath('//*[@class="endofarticle__copyright"]//text()')[0].split('/')[-1]
        except:
            source =""
            
        extractedinfo={"title":title,
                       "byline":author,
                       "byline_source":source,
                       "teaser":teaser,
                       "text":text,
                       "category":category
                       }
        
        return extractedinfo
