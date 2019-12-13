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


class ing(rss):
    """Scrapes ing - Nederland """

    def __init__(self):
        self.doctype = "ing (corp)"
        self.rss_url = (
            "https://www.ing.nl/nieuws/nieuws_en_persberichten/news.xml?format=rss"
        )
        self.version = ".1"
        self.date = datetime.datetime(year=2018, month=10, day=6)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                                
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                
        
        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                               
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                     
            
        yields                                                                                                                                                                                                                                                            
        ---- 
        teaser    the intro to the artcile                                                                                                                                                                                                                                 
        title    the title of the article                                                                                                                                                                                                                                   
        text    the plain text of the article                                                                                                                                                                                                                              
        images: images included in the article
        """

        tree = fromstring(htmlsource)
        try:
            teaser = tree.xpath('//*[@class="intro-text"]//text()')[0]
        except:
            logger.debug("Could not parse article teaser")
            teaser = ""
        try:
            text = "".join(
                tree.xpath('//*[@class="paragraph clearfix"]//text()')
            ).strip()
        except:
            text = ""
            logger.warning("Could not parse article text")
        text = polish(text)
        try:
            title = "".join(tree.xpath('//*[@class="intro"]//h1/text()')).strip()
        except:
            title = ""
            logger.warning("Could not parse article title")

        images = ing._extract_images(self, tree)

        releases = {
            "teaser": teaser.strip(),
            "text": polish(text).strip(),
            "title": title,
            "images": images,
        }
        return releases

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="paragraph clearfix"]//img')
            if len(img_list) > 0:
                img = img_list[0]
                image = {
                    "url": img.attrib["src"],
                    "height": img.attrib["height"],
                    "width": img.attrib["width"],
                }
                #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                #'alt' : img.attrib['alt']}
                if image["url"] not in [i["url"] for i in images]:
                    images.append(image)
            else:
                images = []
        return images
