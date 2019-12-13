# seems to only scrape written questions

import requests
import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
import urllib

logger = logging.getLogger("INCA")


class swedishparliament(rss):
    """Scrapes Swedish Parliament"""

    def __init__(self):
        self.doctype = "swedishparliament (par)"
        self.rss_url = "https://data.riksdagen.se/dokumentlista/?facets=3&del=global&sort=datum&sortorder=desc&doktyp=fr&st=3&datum=2005-01-01&tom=2018-07-11&p=1&fcs=1&utformat=rss"
        self.version = ".1"
        self.BASE_URL = "http://www.riksdagen.se/sv/"
        self.date = datetime.datetime(year=2018, month=6, day=6)

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
        teaser    the intro to the artcile 
        text    the plain text of the article                                                                                                                                                                                                                              
        """

        tree = fromstring(htmlsource)
        try:
            title = "".join(tree.xpath("//h2//text()")).strip()
            logger.debug(title)
        except:
            logger.warning("no title")
            title = ""
        try:
            all_questioners = "".join(
                tree.xpath('//*/p[@class="Av"]/i//text()')
            ).strip()
            questioners = re.sub("[\(].*?[\)]", "", str(all_questioners))
            logger.debug(questioners)
        except:
            all_questioners = ""
            questioners_clean = " ".join(all_questioners.split())
        try:
            questioners_party = re.findall(r"\((.*)\)", all_questioners)[0]
            logger.debug(questioners_party)
        except:
            questioners_party = ""
            questioners_party_clean = " ".join(questioners_party.split())
        try:
            text = " ".join(
                tree.xpath(
                    '//p[@class="Till"]/following-sibling::p/following-sibling::p[.]//text()'
                )
            ).strip()
            logger.debug(text)
        except:
            logger.warning("oops -no text?")
            text = ""
        text = "".join(text)
        releases = {
            "title": title.strip(),
            "text": text.strip(),
            "questioners": questioners.strip(),
            "questioners_party": questioners_party,
        }

        return releases
