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

class faz(rss):
    """Scrapes faz.net"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "faz (www)"
        self.rss_url='http://www.faz.net/rss/aktuell/'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=8, day=3)

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
            category = tree.xpath('//*[@class="gh-LogoStage_Top"]//span/text()')[0]
        except:
            category =""
#teaser
        try:
            teaser = ''.join(tree.xpath('//*[@id="TOP"]//*[@class="atc-IntroText"]//text()')).replace('\n','').replace('\t','')

        except:
            teaser =""
#title
        try:
            title = ''.join(tree.xpath('//*[@class="atc"]//*[@itemprop="headline"]//text()')).replace('\n','').replace('\t','')
        except:
            title =""
            
#text: still has mistakes in it. scrapes more than just the text. also includes adds between the text.

#text1:
        try:
            text1 = tree.xpath('//*[@class="Artikel "]//*[@class="atc-TextFirstLetter"]//text()')

        except:
            text1 =""
#Text2:
        try:
            text2 = ''.join(tree.xpath('//*[@class="Artikel "]//*[@itemprop="articleBody"]/p/text()'))

        except:
            text2 =""
        text = text1 + text2
#author
        try:
            author = ''.join(tree.xpath('//*[@class="atc"]//header//a//text()')).replace('\t','').replace('\n','').strip()
        except:
            author =""
#source
        try:
            source = ''.join(tree.xpath('//*[@class="quelle"]//text()')).replace('Quelle:',"").replace('\r','').replace('\n','')
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
