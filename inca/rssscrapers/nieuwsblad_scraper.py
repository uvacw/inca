import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


def polish(textstring):
    # This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split("\n")
    lead = lines[0].strip()
    rest = "||".join([l.strip() for l in lines[1:] if l.strip()])
    if rest:
        result = lead + " ||| " + rest
    else:
        result = lead
    return result.strip()


class nieuwsblad(rss):
    """Scrapes nieuwsblad.be"""

    def __init__(self):
        self.doctype = "nieuwsblad (www)"
        self.rss_url = "http://feeds.nieuwsblad.be/nieuws/snelnieuws"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                                 
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
        """

        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen", type(doc), len(doc))
            print(doc)
            return ("", "", "", "")
        # category
        try:
            category = tree.xpath('//*[@class="is-active"]/text()')[0]
        except:
            category = ""
            logger.debug("Could not parse article category")
        # text
        try:
            textfirstpara = "".join(
                tree.xpath('//*[@class="article__intro"]/p/text()')
            ).strip()
        except:
            textfirstpara = ""
            logger.debug("Could not parse article teaser")
        try:
            textrest = "".join(
                tree.xpath(
                    '//*[@class="article__body"]/p/text() | //*[@class="article__body"]/p/a/text() | //*[@class="article__body"]/p/strong/text()'
                )
            ).strip()
        except:
            textrest = ""
            logger.warning("Could not parse article text")
        try:
            byline = tree.xpath('//*[@itemprop="author"]/text()')[0]
        except:
            byline = ""
            logger.debug("Could not parse article byline")
        try:
            title = tree.xpath('//*[@class="article__header"]/h1/text()')[0]
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            bylinesource = tree.xpath('//*[@itemprop="sourceOrganization"]/text()')[0]
        except:
            bylinesource = ""
            logger.debug("Could not parse article byline source")

        text = textfirstpara + " " + textrest
        text = text.replace("\xa0", "")
        extractedinfo = {
            "title": title.strip(),
            "text": text.strip(),
            "byline": byline.strip(),
            "bylinesource": bylinesource.strip(),
            "category": category.strip(),
        }

        return extractedinfo
