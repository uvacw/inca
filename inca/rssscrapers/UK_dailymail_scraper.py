import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")
# logger.setLevel(logging.DEBUG)


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


class dailymail(rss):
    """Scrapes dailymail.co.uk"""

    def __init__(self):
        self.doctype = "dailymail (www)"
        self.rss_url = "http://www.dailymail.co.uk/articles.rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=15)

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                                                                                                      
        Parameters                                                                                                                                                               
        ----                                                                                                                                                                       
        htmlsource: string                                                                                                                                                                                                                                                                                                         
        yields
        ----
        title    the title of the article
        teaser    the intro to the artcile
        byline      the author, e.g. "Bob Smith"
        text    the plain text of the article
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Cannot parse HTML tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = "".join(tree.xpath("//*[@id='js-article-text']/h1/text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = ". ".join(
                tree.xpath("//*[@class='mol-bullets-with-font']//text()")
            )
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            byline = " ".join(
                tree.xpath("//*[@class='author-section byline-plain']/a/text()")
            )
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            text = " ".join(
                tree.xpath(
                    "//*[@itemprop='articleBody']/p/text()|//*[@itemprop='articleBody']/p/a/text()"
                )
            )
        except:
            text = ""
            logger.warning("Could not parse article text")

        extractedinfo = {
            "title": title.strip(),
            "teaser": teaser.strip().replace("\xa0", ""),
            "byline": byline.strip().replace("\n", ""),
            "text": text.strip().replace("\xa0", "").replace("\n", ""),
        }

        return extractedinfo

    def parseurl(self, url):
        """
        Parses the category based on the url
        """
        category = url.split("/")[3]
        logger.debug(url)
        logger.debug(category)
        return {"category": category}
