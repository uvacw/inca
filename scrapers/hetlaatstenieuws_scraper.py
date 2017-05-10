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

class hetlaatstenieuws(rss):
    """Scrapes hln.be"""
    
    def __init__(self,database=True):
        self.database=database
        self.doctype = "hetlaatstenieuws"
        self.rss_url= "http://www.hln.be/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=10)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        tree = fromstring(htmlsource)
# byline
        try: 
            byline = tree.xpath('//*[@class="author"]/text()')[0]
            if byline == "":
                logger.info("No author field encountered - don't worry, maybe it just doesn't exist.")
        except:
            byline=""
            logger.info("No 'author' field encountered - don't worry, maybe it just doesn't exist.")
# bylinesource NOG PARSEN!!
        try:
            bylinesource = tree.xpath('//*[@class="author"]/text()')[0]
            if bylinesource == "":
                logger.info("No bylinesource")
        except:
            bylinesource=""
            logger.info("No bylinesource"
# category WERKT NIET!!
        try:
            category = tree.xpath('//*[@class="nieuws_actua_active actua_active"]/text()')[0]  
            if category == "": 
                logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
# title
        try:
            title = tree.xpath('//*[@id="articleDetailTitle"]/text()')[0]
        except:
            logger.info("No title?")
            title=""
# text
        try:
            textfirstpara = tree.xpath('//*[@class="intro"]/text()')[0].replace("\n","").strip()
        except:
            logger.info("No first paragraph")
            textfirstpara=""
        try:
            textrest = " ".join(tree.xpath('//*[@class="clear"]//text()'))
        except:
            logger.info("No text?")
            textrest=""

        texttotal = textfirstpara + " " + textrest
        text = texttotal.replace('(+)','')

        extractedinfo={"byline":byline.replace("bewerkt door:","").strip(),
                       "bylinesource":bylinesource.strip(),
                       "text":text.strip(),
                       "category":category.strip(),
                       "title":title
                       }

        return extractedinfo



