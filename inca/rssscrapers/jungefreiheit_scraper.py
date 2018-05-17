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


class jungefreiheit(rss):
    """Scrapes http://www.jungefreiheit.de/ """

    def __init__(self):
        self.doctype = "junge freiheit (www)"
        self.rss_url='https://jungefreiheit.de/feed/'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=11, day=21)


    def get(self,**kwargs):

        # creating iteration over the rss feed.
        req =request.Request("https://jungefreiheit.de/feed/")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        categories = tree.xpath("//channel//item//category/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")

        for link,category,xpath_date,title,description in zip(article_urls,categories,dates,titles,descriptions):
            link = link.strip()

            try:
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.warning("HTML tree cannot be parsed")


            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@itemprop='text']/p//text()")
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ')

        	# Retrieve author
            try:
            	author = tree.xpath("//span[@class='entry-author-name']/text()")[0].strip()
            except:
            	author = ''


            # source needs to be added. Currently appears in parenthesis at the end of last paragraph.
            last_stnce = parag[-1]
            try:
                source = re.findall(r'(\(.+\))',last_stnce[-15:])[0].replace('(','').replace(')','')
            except:
                source = ''

            # Create iso format date
            try:
                date = datetime.datetime.strptime(xpath_date[5:],"%d %b %Y %H:%M:%S %z").isoformat()
            except:
                date = ''


            doc = dict(
                pub_date    = date,
                title       = title,
                text        = text.strip(),
                summary     = description,
                author      = author,
                source      = source,
                category    = category,
                url         = link,
            )
            doc.update(kwargs)

            yield doc
