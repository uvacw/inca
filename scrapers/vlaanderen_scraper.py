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
# byline
        try: 
            byline = tree.xpath('//*[@class="author-info__name"]/span/text()')[0]
            if byline == "":
                logger.info("No author field encountered - don't worry, maybe it just doesn't exist.")
        except:
            byline=""
            logger.info("No 'author' field encountered - don't worry, maybe it just doesn't exist.")
# bylinesource
        try:
            bylinesource = tree.xpath('//*[@class="author-info__source"]/text()')[0]
            if bylinesource == "":
                logger.info("No bylinesource")
        except:
            bylinesource=""
            logger.info("No bylinesource")
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
            title = tree.xpath('//*[@class="article__header"]/h1/text()')[0]
        except:
            logger.info("No title?")
            title=""
# text
        try:
            textfirstpara = tree.xpath('//*[@class="article__intro fjs-article__intro"]/text()')[0].replace("\n","").strip()
        except:
            logger.info("No first paragraph")
            textfirstpara=""
        try:
            textrest = " ".join(tree.xpath('//*[@class="article__body__paragraph"]//text() | //*[@class="article__body__title"/text()'))
        except:
            logger.info("No text?")
            textrest=""

        texttotal = textfirstpara + " " + textrest
        text = texttotal.replace('(+)','').replace('\xa0','').replace('< Lees een maand gratis alle artikels in onze Pluszone via www.demorgen.be/proef','')

        extractedinfo={"byline":byline.replace("Bewerkt door:","").strip(),
                       "bylinesource":bylinesource.replace("- Bron:","").strip(),
                       "text":text.strip(),
                       "category":category.strip(),
                       "title":title
                       }

        return extractedinfo



