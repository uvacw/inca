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

class gazetvanantwerpen(rss):
    """Scrapes gva.be """

    def __init__(self,database=True):
        self.database=database
        self.doctype = "gazetvanantwerpen (www)"
        self.rss_url= "http://www.gva.be/rss/section/ca750cdf-3d1e-4621-90ef-a3260118e21c"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=3)

    def parsehtml(self,htmlsource):
        '''                                                                                                                                                                                                                                                                 
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                 
        
        Parameters                                                                                                                                                                                                                                                         
        ----                                                                                                                                                                                                                                                                
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                     

        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        category    sth. like economy, sports, ...                                                                                                                                                                                                                      
        text    the plain text of the article                                                                                                                                                                                                                              
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                             
        byline_source    sth like ANP                                                                                                                                                                                                                                       
        '''

        tree = fromstring(htmlsource)

        try:
            byline = tree.xpath('//*[@itemprop="author"]/text()')[0]
            if byline == "":
                logger.info("No author field encountered")
        except:
            byline = ""
            logger.debug("Could not parse article title")
        try:
            bylinesource = tree.xpath('//*[@itemprop="sourceOrganization"]/text()')[0]
        except:
            bylinesource = ""
            logger.debug("Could not parse article byline source")
        try:
            textfirstpara = " ".join(tree.xpath('//*[@class="article__intro"]/p/text()')).strip()
        except:
            textfirstpara = ""
            logger.debug("Could not parse article teaser")
        try:
            textrest = " ".join(tree.xpath('//*[@class="article__body"]/p/text() | //*[@class="article__body"]/p/b/text() | //*[@class="article__body"]/p/i/text() | //*[@class="article__body"]/p/a/text()')).strip()
        except:
            textrest = ""
            logger.warning("Could not parse article text")
        try:
            title = tree.xpath('//*[@class="article__header"]/h1/text()')[0]
            if title == "":
                logger.debug("Could not parse article title?")
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*[@class="is-active"]/text()')[0]
        except:
            category = ""
            logger.debug("Could not parse article category")


        text = textfirstpara + " " + textrest

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "text":text.strip(),
                       "byline":byline.strip(),
                       "bylinesource":bylinesource.strip()
                       }

        return extractedinfo
