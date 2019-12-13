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


class kurier(rss):
    """Scrapes kurier.at"""

    # rss feed different for all categories, only subcategories for nieuws so far included

    def __init__(self):
        self.doctype = "kurier (www)"
        self.rss_url = ["https://kurier.at/xml/rssd"]
        self.version = ".1"
        self.date = datetime.datetime(year=2019, month=9, day=17)

    def get_page_body(self, url):
        """standards.at has a cookie wall which needs to be bypassed by setting a specific cookie in every request."""
        response = requests.get(url, headers={"Cookie": "gdprCookieConsent=true"})
        return response.text

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys
        
        Parameters
        
        htmlsource: string
        yields
        
        title    the title of the article        
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP 
        category    sth. like economy, sports,
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree", type(doc), len(doc))
            # print(doc)
            return ("", "", "", "")
        # category
        try:
            # kurier.at has category tags, usually but not always the first ine
            # is the main one. For now, we only keep the first one
            # but we might consider using other indicators (e.g, url)
            # instead or storing multiple categories as sub-categories.
            category = tree.xpath('//*[@class="tag ng-star-inserted"]/text()')[
                0
            ].strip()
        except:
            category = ""
            logger.debug("Could not parse article category")
        # teaser
        try:
            teaser = (
                "".join(tree.xpath('//*[@class="article-header-leadText-main"]/text()'))
                .strip()
                .replace("\n", "")
            )
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")

        # text
        try:
            text = (
                "".join(tree.xpath('//*[@class="paragraph"]//text()'))
                .strip()
                .replace("\n", "")
            )
        except:
            text = ""
            logger.warninig("Could not parse article text")

        # author
        try:
            author = "".join(tree.xpath('//a[@class="ng-star-inserted"]/text()'))
        except:
            author = ""
            logger.debug("Could not parse article source")

        # bylinesource
        # gives a list with either two or one entries: the first one is the date and if there is a second one it is the bylinesource
        try:

            sourceorganisation = tree.xpath(
                '//*[@class="article-header-intro-right"]/span/text()'
            )

            if len(sourceorganisation) == 2:
                source = sourceorganisation[-1]
            else:
                source = ""
        except:
            source = ""

        # title
        try:
            title = tree.xpath('//*[@class="article-header-title"]/span')[0].text
        except:
            title = ""
            logger.warning("Could not parse article source")

        text = text.replace("\xad", "")
        text = teaser + " " + text
        extractedinfo = {
            "title": title.strip(),
            "text": text.strip(),
            "byline": author.strip(),
            "byline_source": source.strip(),
            "category": category,
            "teaser": teaser,
        }

        return extractedinfo
