from lxml import html
from urllib import request
from lxml.html import fromstring
from scrapers.rss_scraper import rss
from core.scraper_class import Scraper
import re
import feedparser
import logging
import datetime
import requests
from lxml import etree

logger = logging.getLogger(__name__)


class dailymail(rss):
    """Scrapes dailymail.co.uk """

    def __init__(self):
        self.doctype = "dailymail"
        self.rss_url='http://www.dailymail.co.uk/articles.rss'
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
        req =request.Request("http://www.dailymail.co.uk/articles.rss")
        read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")

        for link in article_urls: # you go to each article page       
            link = link.strip()
            try: 
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.error("HTML tree cannot be parsed")
            
            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@class='mol-para-with-font']/font/text() | //*[@class='mol-para-with-font']/font/span/text()")
            text = ''
            for r in parag:
                text += ' '+r.strip()
                #adding a space at the end of the paragraph.
            
            # Retrieving bullet points on top of articles
            bullet = tree.xpath("//*[@class='mol-bullets-with-font']/li/font/strong/text()")
            
            # creating total article_text by merging those two elements.
            article_total = ' '.join(bullet) + ' |||' + text

            # Retrieving the section/category from url
            matchObj = re.match( r'http://www.dailymail.co.uk/(.*?)/(.*?)/', link, re.M|re.I)
            category = matchObj.group(1)

            # Retrieving the byline_source/source from url
            if matchObj.group(1) == 'wires':
                byline_source = matchObj.group(2)
            else:
                byline_source = ''
                
            # Retrieving the byline/author
            byline_tree = tree.xpath("//*[@class='author']/text()")

            # Eliminating anything coming after "for" as in many cases it says "For Mailonline", "For dailymail" etc.
            myreg = re.match('(.*?)( [f|F]or )',', '.join(byline_tree),re.M|re.I)
            if myreg is None:
                author_list = byline_tree
            else:
                author_list = myreg.group(1).split(',')

            # Create iso format date 
            xpath_date = tree.xpath("//*[@class='article-timestamp-published']/text() | //*[@class='byline-section']/span/text()")
            # xpath was troublesome so I only need the last element of the list, minus all the formatting
            select_date = xpath_date[-1].strip()
            # now that we have the date, we just need to tell datetime which values are placed where.
            pub_date = datetime.datetime.strptime(select_date, "%H:%M GMT, %d %B %Y").isoformat()


            title = tree.xpath("//*[@id='js-article-text']//h1/text()")

            doc = dict(
                pub_date    = pub_date,
                title       = title[0],
                text        = text,
                bullet      = bullet[0] if bullet else '',
                author      = author_list,
                source      = byline_source,
                category    = category,
            )
            doc.update(kwargs)
            yield doc
