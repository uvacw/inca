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

class hetbelangvanlimburg(rss):
    """Scrapes hbvl.be"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "het beland van limburg (www)"
        self.rss_url=['http://www.hbvl.be/rss/section/0DB351D4-B23C-47E4-AEEB-09CF7DD521F9','http://www.hbvl.be/rss/section/A160C0A6-EFC9-45D8-BF88-86B6F09C92A6','http://www.hbvl.be/rss/section/FBAF3E6E-21C4-47D3-8A71-902A5E0A7ECB','http://www.hbvl.be/rss/section/18B4F7EE-C4FD-4520-BC73-52CACBB3931B','http://www.hbvl.be/rss/section/3D61D4A0-88CE-44E9-BCE0-A2AD00AD7D2E','http://www.hbvl.be/rss/section/0AECEA6E-9E2F-4509-A874-A2AD00ADEAA4']
        
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
            category = tree.xpath('//*[@class="label label--region"]/text()')
        except:
            category=""
#author
        try:
            author = tree.xpath('//*[@class="article__meta"]//span/text()')
            if len(author) == 2:
                source = author[0]
            else:
                source  = ""
        except:
            source = ""
        try:
            textfirstpara = "".join(tree.xpath('//*[@class="article__intro"]/text()')).strip()
        except:
            textfirstpara = ""
            logger.info('No first paragraph')
        try:
            textrest = "".join(tree.xpath('//*[@class="article__body"]//p/text()'))
        except:
            textrest = ""
        try:
            title = tree.xpath('//*[@class="article__header"]/h1/text()')[0]
        except:
            title = ""
            logger.info('No title?')

        texttotal = textfirstpara + " " + textrest
        extractedinfo={"byline":source,
                       "text":texttotal.strip(),
                       "category":category,
                       "title":title.strip(),
                       }

        return extractedinfo
