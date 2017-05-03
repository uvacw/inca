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


class walmart(rss):
    """Scrapes Walmart """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "walmart (corp)"
        self.rss_url ='http://corporate.walmart.com/rss?feedName=allnews'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=1, day=1)


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
        try:
            title="".join(tree.xpath('//*[@class="article-header-title"]/text()')).strip()
            print("this prints title", title)
        except:
            print("no title")
            title = ""
        try:
            category="".join(tree.xpath('//*[@class="article-header-tags"]//a/text()')).strip()
            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text="".join(tree.xpath('//*[@class="article-content"]/p/text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        text = "\n".join(text)
        try:
             author_door = tree.xpath('//*[@class="article-byline-text"]/p/a/text()')[0].strip()
        except:
            author_door=""
            logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":polish(text).strip(),
                       "byline_source":author_door.replace("\n"," ").strip()
                       }

        return extractedinfo

if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')
