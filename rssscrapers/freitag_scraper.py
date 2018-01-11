from lxml import html
from urllib import request
from lxml.html import fromstring
from scrapers.rss_scraper import rss
from core.scraper_class import Scraper
import re
import feedparser
import logging
import datetime
import locale
import requests
from lxml import etree

logger = logging.getLogger(__name__)


class freitag(rss):
    """Scrapes https://www.freitag.de/ """

    def __init__(self,database=True):
        self.database=database
        self.doctype = "Der Freitag"
        self.rss_url='https://www.freitag.de/@@RSS'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=11, day=21)


    def get(self,**kwargs):

        # creating iteration over the rss feed.
        req =request.Request("https://www.freitag.de/@@RSS")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")


        for link,xpath_date in zip(article_urls,dates):
            link = link.strip()

            try:
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.warning("HTML tree cannot be parsed")

#parsing teaser
            try:
                teaser = tree.xpath("//div[@class='running-text article']/p/span/text() | //div[@class='running-text article']/p/text()")
            except:
                teaser =''

            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//div[@class='text']/p//text()")
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ')

        	# Retrieve author
            try:
            	author = tree.xpath("//div[@class='inner']/aside/h1/a/text()")[0].strip()
            except:
            	author = ''

            title = tree.xpath("//div[@class='running-text article']/h1/text()")


            # source needs to be added. Currently appears in parenthesis at the end of last paragraph.
            source = ''

            # Create iso format date
            try:
                date = datetime.datetime.strptime(xpath_date[5:],"%d %b %Y %H:%M:%S %z").isoformat()
            except:
                date = ''


            doc = dict(
                pub_date    = date,
                title       = title,
                teaser      = teaser,
                text        = parag,
                author      = author,
                source      = source,
                url         = link,
            )
            doc.update(kwargs)

            yield doc
