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


class diewelt(rss):
    """Scrapes http://www.welt.de/ """

    def __init__(self,database=True):
        self.database=database
        self.doctype = "Die Welt"
        self.rss_url='http://www.welt.de/?service=Rss'
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
        req =request.Request("https://www.welt.de/feeds/latest.rss")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        categories = tree.xpath("//channel//item//category/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")
        authors = tree.xpath("//channel//item//author/text()")

        for link,category,xpath_date,title,author in zip(article_urls,categories,dates,titles,authors):      
            link = link.strip()
            try: 
                req_wall = request.Request(link)
                read_wall = request.urlopen(req_wall).read().decode(encoding="utf-8",errors="ignore")
                tree_wall = fromstring(read_wall)
            except:
                logger.error("HTML tree cannot be parsed")


            # For this newspaper there's an extra step in which we need to click on the right link to access the article. 
            if tree.xpath("boolean(//*[@class='o-teaser__title ']/a[3]/@href)"):
                link_end = tree_wall.xpath("//*[@class='o-teaser__title ']/a[3]/@href")[0].strip()
                link = 'https://www.welt.de'+link_end

            
            try:
                req = request.Request(link)
                read = request.urlopen(req).read().decode(encoding="utf-8",errors="ignore")
                tree = fromstring(read)
            except:
                logger.error("HTML tree cannot be parsed")


            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@itemprop='articleBody']/p//text()")
            text = ''
            i = 0
            for r in parag:
                if i < 2:
                    text += ''+r.strip().replace('\xa0',' ')
                    i += 1
                else:
                    text += ' '+r.strip().replace('\xa0',' ')

            # What's this again?
            #tree.xpath('//*[@class="c-article-text c-content-container __margin-bottom--is-0"]//p except [@class="o-element__text o-element__text--is-small"]') 
            
            # Retrieving summary on top of articles
            try:
                summary = tree.xpath("//*[@class='c-summary__intro']/text()")[0].strip()
            except:
                summary = ''

            # Retrieving subcategory
            try:
                subcategory = tree.xpath("//*[@class='o-section c-section ']/text()")[0].strip()
            except:
                subcategory = ''
        
            # Retrieving the byline_source/source from url
            try:
                source = tree.xpath("//*[@class='c-copyright__source']/text()")[0].strip()
            except:
                source = ''
                
            # Retrieving the byline/author if it can be found otherwise, get the one from RSS feed
            if tree.xpath("boolean(//*[@class='c-author__name']/a/text())"):
                author = tree.xpath("//*[@class='c-author__name']/a/text()")[0]

            # Create iso format date 
            #loc= locale.setlocale(locale.LC_ALL, 'de_DE') #Fri, 09 Dec 2016 14:55:39 +0100
            try:
                date = datetime.datetime.strptime(xpath_date[5:],"%d %b %Y %H:%M:%S GMT").isoformat()
            except:
                date = ''

            # Check if it's a paid article and if so return so in the tags
            tags = []
            if tree.xpath("boolean(//*[@data-external-component='Premium.Article.Content'])"):
                tags.append('paid')
            # doing the same if it's a video as there's usually no text accompanying. 
            if tree.xpath("boolean(//*[@class='c-video-article-content'])"):
                tags.append('video') 


            doc = dict(
                pub_date    = date,
                title       = title,
                text        = text.strip(),
                summary     = summary,
                author      = author,
                source      = source,
                category    = category,
                subcategory = subcategory,
                tags        = tags,
                url         = link,
            )
            doc.update(kwargs)
            
            yield doc        
         
