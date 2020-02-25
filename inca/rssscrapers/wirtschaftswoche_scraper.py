import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")

class wirtschaftswoche(rss):
    """Scrapes wiwo.de"""

    def __init__(self):
        self.doctype = "wiwo (www)"
        self.rss_url='http://www.wiwo.de/contentexport/feed/rss/schlagzeilen'
        self.version = ".1"
        self.date    = datetime.datetime(year=2018, month=5, day=2)

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
            logger.warning("HTML tree cannot be parsed")
#teaser
        try:
            teaser = tree.xpath('//*[@class="c-leadtext u-font-semibold u-margin-xl"]/text()')[0]
        except:
            teaser = ""


#text:
        try:
            text = " ".join(tree.xpath('//*[@class="u-richtext ajaxify"]/p/a/text()|//*[@class="u-richtext ajaxify"]/p/text()'))
        except:
            text = ""

#author
        try:
            author = " ".join(tree.xpath('//*[@class="c-metadata u-margin-xl "]/div/a/text()|//*[@class="c-metadata u-margin-xl "]/div//span/text()|//*[@class="c-metadata u-margin-xl u-margin-xxxl"]/div//span/text()|//*[@class="u-float-left u-margin-left-l "]//span/text()')).replace("\n", "")
        except:
            author =""

#title

        try:
            title = "".join(tree.xpath('//*[@class="c-headline c-headline--article u-margin-m"]/text()|//*[@class="o-article__element"]//h2/text()')).replace("\n", "")
        except:
            title = ""
#source
        try:
            source="".join(tree.xpath('//*[@class="c-metadata u-margin-xl"]/a/span/text()'))   
        except:
            source = ""

#category

        try:
            category = " ".join(tree.xpath('//*[@class="c-nav__breadcrumbs"]//li/a/span/text()')).replace("WiWo ","").replace(" ",": ")                                             
        except:
            category = ""
            
        extractedinfo={"title":title,
                       "text":text,
                       "teaser":teaser,
                       "category":category,
                       "byline":author,
                       "byline_source":source
                       }

        return extractedinfo
