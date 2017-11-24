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


class taz(rss):
    """Scrapes http://www.taz.de"""

    def __init__(self,database=True):
        self.database = database
        self.doctype = "die tageszeitung"
        self.rss_url='http://www.taz.de/!p4608;rss/'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=12, day=25)
    

    def get(self,**kwargs):

        # creating iteration over the rss feed. 
        req =request.Request("http://www.taz.de/!p4608;rss/")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        categories = tree.xpath("//channel//item//category/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")

        for link,xpath_date,title in zip(article_urls,dates,titles):      
            link = link.strip()
            
            try:
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.error("HTML tree cannot be parsed")


            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//p[@class='article first odd']/text() | //p[@class='article odd']/text() | //p[@class='article even']/text() | //*[@class='sectbody']/h6//text()")
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ').replace('| ','')
        
            # Retrieve author    
            try:
                author = tree.xpath("//*[@class='rack first_rack']/div/div/a/h4/text()")[0].strip()
            except:
                author = ''

            # Retrieve source, which is usually the second word of articles containing it, nested inside an <em> element.
            try:
                if tree.xpath("boolean(//*[@class='article first odd']/em/text())"):
                    # Using this arbitrary 15 len character to differentiate the potential existence of a researcher description vs. an actual source. The mag doesn't provide class to differentiate. 
                    if len(tree.xpath("//*[@class='article first odd']/em/text()")[0]) < 15:
                        source = tree.xpath("//*[@class='article first odd']/em/text()")[0].strip().replace('(','').replace(')','')
                    else:
                        source = ''
                else:
                    source = ''
            except:
                source = ''

            # Summary as first paragraph of "text"
            try:
                description = tree.xpath("//*[@class='sectbody']/p/text()")[0].strip()
            except:
                description = ''

            #Category
            try:
                category_list = tree.xpath("//*[@class='left rootline toolbar']/li//text()")
                category = ', '.join(category_list)
            except:
                category = ''

            # Create iso format date 
            try:
                # 25 Dec 2016 12:37:00 +0100    
                date = datetime.datetime.strptime(xpath_date,"%d %b %Y %H:%M:%S %z").isoformat()
            except:
                date = ''


            doc = dict(
                pub_date    = date,
                title       = title,
                text        = text.strip(),
                teaser     = description,
                byline      = author,
                source      = source,
                category    = category,
                url         = link,
            )
            doc.update(kwargs)
            
            yield doc        
