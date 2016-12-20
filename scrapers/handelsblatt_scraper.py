
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


class handelsblatt(rss):
    """Scrapes http://www.handelsblatt.com/ """

    def __init__(self):
        self.doctype = "Handelsblatt"
        self.rss_url='http://www.handelsblatt.com/contentexport/feed/schlagzeilen'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=11, day=21)
    

    def get(self,**kwargs):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        # creating iteration over the rss feed. 
        req =request.Request("http://www.handelsblatt.com/contentexport/feed/schlagzeilen")
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
                logger.error("HTML tree cannot be parsed")


            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@class='vhb-article-content']/p//text()")
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ')

            # Handling the potential 2nd page
            if tree.xpath("boolean(//*[@class='vhb-table-list']/a[1])"):
                next_page = tree.xpath("//*[@class='vhb-table-list']/a/@href")[0]
                next_page_link = 'http://www.handelsblatt.com'+next_page
                req2 = request.Request(next_page_link)
                read2 = request.urlopen(req2).read().decode(encoding="utf-8",errors="ignore")
                tree2 = fromstring(read2)
                parag2 = tree2.xpath("//*[@class='vhb-article-content']/p//text()")
                for r in parag2:
                    text += ' '+r.strip().replace('\xa0',' ')

                # check for 3rd page
                if tree.xpath("boolean(//*[@class='vhb-table-list']/a[2])"):
                    next_page = tree.xpath("//*[@class='vhb-table-list']/a/@href")[0]
                    next_page_link = 'http://www.handelsblatt.com'+next_page
                    req3 = request.Request(next_page_link)
                    read3 = request.urlopen(req3).read().decode(encoding="utf-8",errors="ignore")
                    tree3 = fromstring(read3)
                    parag3 = tree3.xpath("//*[@class='vhb-article-content']/p//text()")
                    for r in parag3:
                        text += ' '+r.strip().replace('\xa0',' ')
        
            # Retrieving the byline_source/source from url
            if tree.xpath("boolean(//*[@class='vhb-author-content-name']/text())"):
                source = tree.xpath("//*[@class='vhb-author-content-name']/text()")[0].strip()
            else:
                source = ''
            
            author = ''
            # Retrieving the byline/author if it can be found otherwise, get the one from RSS feed
            # there are no authors in this online newspaper

            # Create iso format date 
            #loc= locale.setlocale(locale.LC_ALL, 'de_DE') #Fri, 09 Dec 2016 14:55:39 +0100
            
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
