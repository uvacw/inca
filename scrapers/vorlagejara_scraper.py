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

class ad(rss):
    """Scrapes ad.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "ad (www)"
        self.rss_url='http://www.ad.nl/rss.xml'
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
            category = tree.xpath('//*[@class="container"]/h1/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        #1. path: regular intro                                                                                                    
        #2. path: intro when in <b>; found in a2014 04 130                                                                         
        textfirstpara=tree.xpath('//*[@id="detail_content"]/p/text() | //*[@class="intro"]/b/text() | //*[@class="intro"]/span/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text()')
        if textfirstpara=="":
            logger.info("OOps - geen eerste alinea?")
        #1. path: regular text                                                                                                     
        #2. path: text with link behind (shown in blue underlined); found in 2014 12 1057                                          
        #3. path: second hadings found in 2014 11 1425   
        textrest = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*[@class="article__paragraph"]/span/text() | //*[@id="detail_content"]/section/p/a/text() | //*[@id="detail_content"]/section/p/strong/text() | //*/p[@class="article__paragraph"]/strong/text()')
        if textrest=="":
            logger.info("OOps - empty textrest")
        text = "\n".join(textfirstpara) + "\n" + "\n".join(textrest)
        try:
            author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
        text=polish(text)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
