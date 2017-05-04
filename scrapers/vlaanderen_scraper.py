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

class demorgen(rss):
    """Scrapes demorgen.de """
    
    def __init__(self,database=True):
        self.database=database
        self.doctype = "demorgen (www)"
        self.rss_url= "http://www.demorgen.be/nieuws/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=3)

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
# author
        try: 
            author_door = tree.xpath('//*[@class="author-info__name"]/text()')[0]
            if author_door == "":
                logger.info("No author field encountered - don't worry, maybe it just doesn't exist.")
        except:
            author_door=""
            logger.info("No 'author' field encountered - don't worry, maybe it just doesn't exist.")
# category
        try:    
            category = tree.xpath('//*[@class="breadcrumb__link first last"]/text()')[0]
            if category == "":    # the category can also contain two sections, then it will be in [@class="breadcrumb__link last"]
                logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
# title
        try:
            title = " ".join(tree.xpath('//h1/text()'))
            if textrest == "":
                logger.info("No title?")
        except:
            logger.info("No title?")
            title=""
# teaser
        try:
            teaser = tree.xpath('//*[@class="article__intro fjs-article__intro"]/text()')[0]
        except:
            logger.info("No teaser")
            teaser=""

        extractedinfo={"byline":author_door.strip(),
                       "category":category.strip(),
                       "title":title.strip(),
                       "teaser":teaser.strip()
                       }

        return extractedinfo



