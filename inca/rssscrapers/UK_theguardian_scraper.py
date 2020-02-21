import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
import requests

logger = logging.getLogger("INCA")

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class theguardian(rss):
    """Scrapes theguardian.com"""

    def __init__(self):
        self.doctype = "theguardian (www)"
        self.rss_url = "https://www.theguardian.com/uk/rss"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=13)

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
        teaser    the intro to the artcile                                                                                                                                                             
        byline    the author, e.g. "Bob Smith" 
        category    sth. like economy, sports, ...                                                                                                                                                                                                                           
        text    the plain text of the article                                                                                                                                                                                                                               
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not HTML tree",type(doc),len(doc))
            #logger.warning(doc)
            return("","","", "")
        try:
            title = ''.join(tree.xpath("//*[@class='gs-container']//h1//text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = tree.xpath("//*[@class='content__standfirst']//text()|//*[@class='content__standfirst content__standfirst--immersive-article']//p//text()|//*[@class='content__standfirst content__standfirst--gallery']//p//text()")
        except:
            teaser = ""
            logger.debug("Could not parse article title")
        try:
            byline = " ".join(tree.xpath("//*[@class='byline']//text()|//*[@itemprop='name']//text()|//*[@class='content__standfirst content__standfirst--immersive-article']/p[2]/text()"))
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            category = tree.xpath("//*[@class='label__link-wrapper']//text()")  
        except:
            category = ""
            logger.debug("Could not parse article category")
        
        try:
            text = " ".join(tree.xpath("//*[@itemprop='articleBody']/p/text()|//*[@itemprop='articleBody']//a/text()|//*[@itemprop='reviewBody']/p/text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")


        extractedinfo={"title":title.replace("\n",""),
                       "teaser":teaser,
                       "byline":byline.strip().replace("\n",""),
                       "category":category,
                       "text":text.replace("\\","")
                      }

        return extractedinfo
