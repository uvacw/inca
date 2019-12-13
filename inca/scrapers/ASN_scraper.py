import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")

MAAND2INT = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}


class asn(Scraper):
    """Scrapes asn"""

    def __init__(self):
        self.START_URL = "https://www.asnbank.nl/nieuws-pers.html"
        self.BASE_URL = "https://www.asnbank.nl"
        self.doctype = "asn (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=11, day=10)

    def get(self, save):
        """                                                                             
        Fetches articles from ASN
        """

        releases = []
        tree = fromstring(requests.get(self.START_URL).text)

        linkobjects = tree.xpath('//*[@class="title"]//a')
        links = [self.BASE_URL + l.attrib["href"] for l in linkobjects]

        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            # this saves the html source:
            htmlsource = requests.get(link).text
            tree = fromstring(htmlsource)
            try:
                title = "".join(
                    tree.xpath('//*[@class="h1-wrapper"]/h1//text()')
                ).strip()
            except:
                # print("no title")
                title = ""
            try:
                try:
                    d = tree.xpath('//*[@class="intro"]//text()')[1].strip()
                except:
                    d = tree.xpath('//*[@class="intro"]//text()')[0].strip()
                jaar = int(d[-4:])
                maand = MAAND2INT[d[13:-4].strip()]
                dag = int(d[10:13])
                datum = datetime.datetime(jaar, maand, dag)
            # except:
            #    d = tree.xpath('//*[@class="intro"]//text()')[0].strip()
            #    jaar = int(d[-4:])
            #    maand = MAAND2INT[d[13:-4].strip()]
            #    try:
            #        dag = int(d[10:-13])
            #    except:
            #        dag = int(d[10:-14])
            #    datum = datetime.datetime(jaar,maand,dag)
            except Exception as e:
                print("could not parse date")
                print(e)
                datum = None
            try:
                teaser = "".join(tree.xpath('//*[@class="intro"]/p//text()')).strip()
            except:
                # print("no teaser")
                teaser = ""
                teaser_clean = " ".join(teaser.split())
            try:
                text = "".join(
                    tree.xpath('//*[@class="article-default"]//text()')
                ).strip()
            except:
                # print("geen text")
                logger.info("oops - geen textrest?")
                text = ""
            try:
                share = "".join(tree.xpath('//*[@class="h2-wrapper"]//text()')).strip()
            except:
                share = ""
            text = "".join(text)
            # cleaning up text: remove teaser and sharing
            textzonderteaser = text[len(teaser) :]
            textclean = textzonderteaser[: -len(share)]
            releases.append(
                {
                    "title": title.strip(),
                    "teaser": teaser.strip(),
                    "text": textclean.strip(),
                    "htmlsource": htmlsource,
                    "publication_date": datum,
                    "url": link,
                }
            )

        return releases
