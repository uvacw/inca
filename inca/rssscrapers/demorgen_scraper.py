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


class demorgen(rss):
    """Scrapes demorgen.de """

    def __init__(self):
        self.doctype = "demorgen (www)"
        self.rss_url = "http://www.demorgen.be/nieuws/rss.xml"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=5, day=3)

    def parsehtml(self, htmlsource):
        """
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        """

        tree = fromstring(htmlsource)
        try:
            byline = tree.xpath('//*[@class="author-info__name"]/span/text()')[0]
            if byline == "":
                logger.debug("Could not parse article source")
        except:
            byline = ""
            logger.debug("Could not parse article source")
        try:
            bylinesource = tree.xpath('//*[@class="author-info__source"]/text()')[0]
            if bylinesource == "":
                logger.debug("Could not parse article source byline")
        except:
            bylinesource = ""
            logger.debug("Could not parse article source byline")
        # two different paths for category:
        # path 1: when the category exists of a main category and a specific category (only second one needed)
        # path 2: when there is just one category
        try:
            cat = tree.xpath('//*[@class="breadcrumb__link first last"]/text()')
            if cat == "":
                try:
                    category = tree.xpath('//*[@typeof="v:Breadcrumb"]/a/text()')[-1]
                except:
                    logger.debug("Could not parse article category")
                    category = ""
            else:
                try:
                    category = tree.xpath(
                        '//*[@class="breadcrumb__link first last"]/text()'
                    )[0]
                except:
                    logger.debug("Could not parse article category")
                    category = ""
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            maintitle = tree.xpath('//*[@class="article__header"]/h1/text()')[0]
        except:
            logger.warning("Could not parse article title")
            maintitle = ""
        try:
            subtitle = tree.xpath('//*[@class="article__header"]/p/text()')[0]
        except:
            subtitle = ""
            logger.debug("Could not parse article subtitle")
        try:
            body = " ".join(
                tree.xpath('//*[@class="article__body__paragraph"]//text()')
            )
        except:
            logger.warning("Could not parse article text")
            body = ""
        # two different paths, since the first paragraph is sometimes in the header, meaning it is a teaser.
        # path 1: when the first paragraph is actually the first paragraph
        # path 2: when the first paragraph is the teaser (teaser is then embedded in one part together with the subtitle)
        try:
            teaser = "".join(
                tree.xpath(
                    '//*[@class="article__header"]/p//text() | //*/p[@class="article__intro fjs-article__intro"]//text()'
                )
            ).replace("\xa0", "")
            if teaser == []:
                # article type A
                try:
                    textfirstpara = tree.xpath(
                        '//*[@class="article__body fjs-article__body"]/p/text()'
                    ).strip()[0]
                except:
                    logger.debug("Could not parse article teaser")
                    textfirstpara = ""
            else:
                # article type B
                try:
                    intro = "".join(
                        tree.xpath('//*[@class="article__header"]/p/text()')[1:]
                    )
                    textfirstpara = ""
                except:
                    intro = ""
                    textfirstpara = ""
                    logger.debug("Could not parse article teaser")
        except:
            teaser = ""

        title = maintitle + " \n" + subtitle
        text = (
            body.replace("(+)", "")
            .replace("\xa0", "")
            .replace(
                "< Lees een maand gratis alle artikels in onze Pluszone via www.demorgen.be/proef",
                "",
            )
        )

        extractedinfo = {
            "byline": byline.replace("Bewerkt door:", "").strip(),
            "bylinesource": bylinesource.replace("- Bron:", "").strip(),
            "text": text.strip(),
            "category": category.strip(),
            "title": title.strip(),
            "teaser": teaser.strip(),
        }

        return extractedinfo
