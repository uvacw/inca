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
        
        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                     

        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                              
        byline_source    sth like ANP                                                                                                                                                                                                                                       
        category    sth. like economy, sports, ...                                                                                                                                                                                                                          
        '''
        
        tree = fromstring(htmlsource)
        try:
            teaser = "".join(tree.xpath('//*[@class="subtitulo gris-oscuro"]/text()')).strip()
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            title_header="".join(tree.xpath('//*[@class="antetitulo-noticia gris-medio"]/text()')).strip()
        except:
            logger.warning("Could not parse article title")
            title = ""
        try:
            title_under = "".join(tree.xpath('//*[@class="titulo-noticia"]/text()')).strip()
        except:
            title_under = ""
        title = title_header + "\n" + "\n" + title_under
        try:
            author_raw = tree.xpath('//*[@class="bloque"]/a[@class="alter"]//strong//text()')
        except:
            author_raw = ""
        author = " & ".join(author_raw[:-1]).strip()
        try:
            category= author_raw [-1].strip()
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            text ="".join(tree.xpath('//*[@class="col-A cuerpo-articulo gris-ultra-oscuro"]//div//text()')).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        extractedinfo={"title":title.strip(),
                       "author":author.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip(),
                       "teaser":teaser.strip()
                       }

        return extractedinfo


class elpais(rss):
    """Scrapes elpais"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "elpais (www)"
        self.rss_url ='http://ep00.epimg.net/rss/elpais/portada.xml'
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
            title_header="".join(tree.xpath('//*[@class="articulo-titulo "]/text()')).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            title_under = "".join(tree.xpath('//*[@class="articulo-subtitulos"]//text()')).strip()
        except:
            title_under = ""
        title = title_header + "\n" + "\n" + title_under
        try:
            author = "".join(tree.xpath('//*[@class="autor-texto"]//a/text()')).strip().replace("Twitter", "")
        except:
            author = ""
            logger.debug("Could not parse article source")
        try:
            category = "".join(tree.xpath('//*[@class="enlace"]//text()')[1]).strip()
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            text ="".join(tree.xpath('//*[@class="articulo-cuerpo"]//text()')).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        extractedinfo={"title":title.strip(),
                       "author":author.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip(),
                       }

        return extractedinfo

class elmundo(rss):
    """Scrapes elmundo"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "elmundo (www)"
        self.rss_url ='http://estaticos.elmundo.es/elmundo/rss/portada.xml'
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
            title ="".join(tree.xpath('//*[@class="js-headline"]/text()')).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = "\n".join(tree.xpath('//*[@class="subtitle-items"]//text()')).strip()
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            author = "".join(tree.xpath('//*[@class="author-name"]//text()')).strip().replace("| ","\n")
        except:
            author = ""
            logger.debug("Could not parse article source")
        try:
            category = "".join(tree.xpath('//*[@class="first-level"]//text()')).strip()
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            text = "".join(tree.xpath('//*[@itemprop="articleBody"]//p/text()')).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "author":author.strip(),
                       "category":category.strip(),
                       "text":polish(text).strip(),
                       }

        return extractedinfo

if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')
