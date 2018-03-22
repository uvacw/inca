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


class jungewelt(rss):

    def __init__(self,database=True):
        self.database = database
        self.doctype = "jungewelt"
        self.rss_url='https://www.jungewelt.de/feeds/newsticker.rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=12, day=28)


    def get(self,**kwargs):

        # creating iteration over the rss feed.
        req =request.Request("https://www.jungewelt.de/feeds/newsticker.rss")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        categories = tree.xpath("//channel//item//category/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")

        for link,xpath_date,title,category,description in zip(article_urls,dates,titles,categories,descriptions):
            link = link.strip()

            try:
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.warning("HTML tree cannot be parsed")


            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@class='Content']/p//text()")
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ').replace('| ','')


            # Retrieve source, which is usually the second word of articles containing it, nested inside an <em> element.
            try:
                # check if a sequence of something inside parenthesis () exists, as it is the way that the source is setup for this magazine
                m = re.search("(\\(.+\\))",tree.xpath("//*[@class='Content']/p[last()-1]/text()")[0],re.M|re.I)
                if m.group(1):
                    # Using this arbitrary 15 len character to differentiate the potential existence of a researcher description vs. an actual source. The mag doesn't provide class to differentiate.
                    if len(m.group(1)) < 15 and m.group(1) not in ['(...)','(CDU)']:
                        source = m.group(1)
                    else:
                        source = ''
                else:
                    source = ''
            except:
                source = ''

            try:
                author = tree.xpath("//*[@class='Article']/address/text()")[0].replace('Von ','')
            except:
                author = ''

            # Create iso format date
            try:
                # Wed, 28 Dec 2016 06:56:52 +0100
                date = datetime.datetime.strptime(xpath_date[5:],"%d %b %Y %H:%M:%S %z").isoformat()
            except:
                date = ''

            tags = []
            if tree.xpath("boolean(//div[@id='ID_LoginFormFailed'])"):
                tags.append('paid')

            doc = dict(
                pub_date    = date,
                title       = title,
                text        = text.strip(),
                summary     = description,
                source      = source,
                category    = category,
                url         = link,
                tags        = tags,
            )
            doc.update(kwargs)

            yield doc
