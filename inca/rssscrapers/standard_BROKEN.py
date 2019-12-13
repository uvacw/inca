import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
import requests

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


class standard(rss):
    """Scrapes standard.at"""

    # rss feed different for all categories, only subcategories for nieuws so far included

    def __init__(self):
        self.doctype = "standard (www)"
        self.rss_url = ["http://www.standard.at/rss"]
        self.version = ".1"
        self.date = datetime.datetime(year=2019, month=9, day=17)

    def get_page_body(self, url):
        """standards.at has a cookie wall which needs to be bypassed by setting a specific cookie in every request."""
        response = requests.get(url, headers={"Cookie": "DSGVO_ZUSAGE_V1=true"})
        return response.text

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
            logger.warning("Could not parse HTML tree", type(doc), len(doc))
            # print(doc)
            return ("", "", "", "")
        # category
        try:
            category = tree.xpath("//ol/li[3]/a/b/text()")
        except:
            category = ""
            logger.debug("Could not parse article category")
        # teaser
        try:
            textfirstpara = "".join(
                tree.xpath(
                    '//*[@class="article-full"]/*[@class="article__body"]/*[@class="intro"]//text()'
                )
            ).strip()
        except:
            textfirstpara = ""
            logger.debug("Could not parse article teaser")

        # text
        try:
            text = "".join(
                tree.xpath(
                    '//*[@class="article-full"]//*[@class="article__body"]/p/text()'
                )
            )
        except:
            text = ""
            logger.warninig("Could not parse article text")

        # author
        try:
            author = "".join(tree.xpath('//*[@itemprop="author"]/text()'))
        except:
            author = ""
            logger.debug("Could not parse article source")

        # bylinesource
        # gives a list with either two or one entries: the first one is the date and if there is a second one it is the bylinesource
        try:
            sourceorganisation = tree.xpath('//*[@class="blend-in"]/text()')
            if len(sourceorganisation) == 2:
                source = sourceorganisation[-1]
            else:
                source = ""
        except:
            source = ""
        try:
            title = tree.xpath('//*[@itemprop="name"]/text()')[0]
        except:
            title = ""
            logger.warning("Could not parse article source")

        text = text.replace("\xad", "")
        text = textfirstpara + " " + text
        extractedinfo = {
            "title": title.strip(),
            "text": text.strip(),
            "byline": author.strip(),
            "byline_source": source.strip(),
            "category": category,
        }

        return extractedinfo
