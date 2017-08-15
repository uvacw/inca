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

class detijd(rss):
    """Scrapes tijd.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "detijd (www)"
        self.rss_url=['http://www.tijd.be/rss/ondernemen.xml','http://www.tijd.be/rss/politiek.xml','http://www.tijd.be/rss/markten_live.xml','http://www.tijd.be/rss/opinie.xml','http://www.tijd.be/rss/cultuur.xml','http://www.tijd.be/rss/netto.xml','http://www.tijd.be/rss/sabato.xml']
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
        try:
             author = tree.xpath('//*[@class="m-meta__item-container"]//a/text()')[0]
        except:
             author = ""
        try:
            textfirstpara = tree.xpath('//*[@class="l-main-container-article__intro highlightable "]/text()').strip()
        except:
            textfirstpara = ""
            logger.info('No first paragraph?')
        try:
            textrest = "".join(tree.xpath('//*[@class="l-main-container-article__body clearfix highlightable "]//text()')).strip()
        except:
            textrest =""
            logger.info('No text?')
        try:
            category = tree.xpath('//*[@class="m-breadcrumb__item--last"]/a/span/text()')[0]
        except:
            category =""
            logger.info('No category')
        try:
            title = "".join(tree.xpath('//*[@class="l-grid__item desk-big-five-sixths push-desk-big-one-sixth"]//text()')).strip()
        except:
            title = ""
            logger.info('No title')

        texttotal = textfirstpara + " " + textrest
        extractedinfo={"byline":author.strip(),
                       "text":texttotal.strip(),
                       "category":category.strip(),
                       "title":title,
                       }

        return extractedinfo
