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


class zeit(rss):

    def __init__(self):
        self.doctype = "http://zeit.de"
        self.rss_url='http://newsfeed.zeit.de/index'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=12, day=28)
    

    def get(self,**kwargs):

        # creating iteration over the rss feed. 
        req =request.Request("http://newsfeed.zeit.de/index")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        categories = tree.xpath("//channel//item//category/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")

        for link,xpath_date,title,category in zip(article_urls,dates,titles,categories):      
            link = link.strip()
            
            try:
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.error("HTML tree cannot be parsed")


            # if article contains multiple plages, go ahead and open the full article in one page:
            if tree.xpath("boolean(//*[@class='article-pager__all']/a/@href)"):
                link = tree.xpath("//*[@class='article-pager__all']/a/@href")[0].strip()
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)

            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@class='article-page']/p//text() | //*[@class='entry-content']/p//text() | //*[@itemprop='articleBody']/section/h2//text() | //*[@itemprop='articleBody']/section/p//text() ")
            text = ''
            for r in parag:
                if len(r) > 0:
                    text += ' '+r.strip().replace('\xa0',' ').replace('| ','')
            text = ''.join(text.splitlines()).strip()

            # Retrieve source, which is usually the second word of articles containing it, nested inside an <em> element.
            try:
                source = tree.xpath("//*[@class='metadata__source']/text()")[0].replace('Quelle: ','')
            except:
                source = ''

            try:
                author = tree.xpath("//*[@class='author vcard']/a/text() | //*[@itemprop='author']/a/span/text()")[0]
            except:
                author = ''

            try:
                description = tree.xpath("//*[@class='summary']/text()")[0].strip()
            except:
                description = ''

            # Create iso format date 
            try:
                # Wed, 28 Dec 2016 06:56:52 +0100
                date = datetime.datetime.strptime(xpath_date[5:],"%d %b %Y %H:%M:%S %z").isoformat()
            except:
                date = ''


            doc = dict(
                pub_date    = date,
                title       = title,
                text        = text.strip(),
                summary     = description,
                source      = source,
                category    = category,
                url         = link,
            )
            doc.update(kwargs)
            
            yield doc        
