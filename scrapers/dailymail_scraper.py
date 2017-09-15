import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class dailymail(rss):
    """Scrapes dailymail.co.uk"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "dailymail (www)"
        self.rss_url='http://www.dailymail.co.uk/articles.rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=15)
        
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
            logger.warning("cannot parse?",type(doc),len(doc))
            logger.warning(doc)
            return("","","", "")
        try:
            title = "".join(tree.xpath("//*[@id='js-article-text']/h1/text()"))
        except:
            title = ""
            logger.info("No 'title' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            teaser = ". ".join(tree.xpath("//*[@class='mol-bullets-with-font']//text()"))
        except:
            teaser = ""
            logger.info("No 'teaser' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            byline = " ".join(tree.xpath("//*[@class='author-section byline-plain']/a/text()"))
        except:
            byline = ""
            logger.info("No 'byline' field encountered - don't worry, maybe it just doesn't exist.")    
        try:
            text = "".join(tree.xpath("//*[@itemprop='articleBody']/p/text()|//*[@itemprop='articleBody']/p/a/text()"))
        except:
            text = ""
            logger.info("No 'text' field encountered - don't worry, maybe it just doesn't exist.")
            
    
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip().replace("\xa0",""),
                       "byline":byline.strip().replace("\n",""),
                       "text":text.strip().replace("\xa0","").replace("\n","")
                      }

        return extractedinfo 
    
    def parseurl(self,url):
        '''
        Parses the category based on the url
        '''
        category = url.split("/")[3]
        logger.debug(url)
        logger.debug(category)
        return {"category": category}

        