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


class abc(rss):
    """Scrapes abc """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "abc (www)"
        self.rss_url ='http://www.abc.es/rss/feeds/abcPortada.xml'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=5, day=10)


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
            teaser = "".join(tree.xpath('//*[@class="subtitulo gris-oscuro"]/text()')).strip()
            print("this prints teaser", teaser)
        except:
            teaser = ""
        try:
            title_header="".join(tree.xpath('//*[@class="antetitulo-noticia gris-medio"]/text()')).strip()
        except:
            print("no title")
            title = ""
        try:
            title_under = "".join(tree.xpath('//*[@class="titulo-noticia"]/text()')).strip()
#           print("this prints title", title)
        except:
            print("no title")
            title_under = ""
        title = title_header + "\n" + "\n" + title_under
        print("this prints title", title)
        try:
            author_raw = tree.xpath('//*[@class="bloque"]/a[@class="alter"]//strong//text()')
        except:
            author_raw = ""
        author = " & ".join(author_raw[:-1]).strip()
        print("this prints author:", author)
        try:
            category= author_raw [-1].strip()
            print("this prints category", category)
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text ="".join(tree.xpath('//*[@class="col-A cuerpo-articulo gris-ultra-oscuro"]//div//text()')).strip()
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            text = ""
        print("this prints text", text)
        extractedinfo={"title":title.strip(),
                       "author":author.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip(),
                       "teaser":teaser.strip()
                       }

        return extractedinfo


if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')
