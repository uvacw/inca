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


class tagesspiegel(rss):
    """Scrapes http://www.handelsblatt.com/ """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "DerTagesspiegel"
        self.rss_url='http://www.tagesspiegel.de/contentexport/feed/home'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=11, day=21)
    

    def get(self,**kwargs):

        # creating iteration over the rss feed. 
        req =request.Request("http://www.tagesspiegel.de/contentexport/feed/home")
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
            parag = tree.xpath("//*[@itemprop='articleBody']/p//text()")
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ')

			# Handling the potential 2nd page
            if tree.xpath("boolean(//*[@class='ts-link ts-next-page'])"):
                next_page = tree.xpath("//*[@class='ts-link ts-next-page']/@href")[0]
                next_page_link = 'http://www.tagesspiegel.de'+next_page
                req2 = request.Request(next_page_link)
                read2 = request.urlopen(req2).read().decode(encoding="utf-8",errors="ignore")
                tree2 = fromstring(read2)
                parag2 = tree2.xpath("//*[@itemprop='articleBody']/p//text()")
                for r in parag2:
                    text += ' '+r.strip().replace('\xa0',' ')

            # Determining if we're dealing with an article or a debate. 
            if tree.xpath("boolean(//*[@class='dp-debate-summary'])"):
            	article_format = 'Debate'
            else:
            	article_format = 'Article'
        
        	# Retrieve author    
            try:
            	author = tree.xpath("//*[@class='dp-author-name']/text() | //*[@class='dp-moderator-name']/text() | //*[@class='ts-authors']/a/text()")[0].strip()
            except:
            	author = ''

            if tree.xpath("boolean(//*[@class='dp-debate-summary'])"):
            	moderators = tree.xpath("//*[@class='dp-moderator-name']/text()")[1:]
            else:
            	moderators = ''

            # Retrieve source, which is in parenthesis at the end of last paragraph. Check if there are multiple pages, in which case we get it from last page.
            try:
            	if tree.xpath("boolean(//*[@class='ts-link ts-next-page'])"):
            		# Using this arbitrary 15 len character to differentiate the potential existence of a researcher description vs. an actual source. The mag doesn't provide class to differentiate. 
            		if len(tree2.xpath("(//*[@itemprop='articleBody']/p)[last()]/em/text() | //*[@itemprop='articleBody']/p/em/text()")[0]) < 15:
            			source = tree2.xpath("(//*[@itemprop='articleBody']/p)[last()]/em/text() | //*[@itemprop='articleBody']/p/em/text()")[0].strip().replace('(','').replace(')','')
            		else:
            			source = ''
            	else:
            		if len(tree.xpath("(//*[@itemprop='articleBody']/p)[last()]/em/text() | //*[@itemprop='articleBody']/p/em/text()")[0]) < 15:
            			source = tree.xpath("(//*[@itemprop='articleBody']/p)[last()]/em/text() | //*[@itemprop='articleBody']/p/em/text()")[0].strip().replace('(','').replace(')','')
            		else:
            			source = ''
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
                format      = article_format,
                source      = source,
                moderators  = moderators,
                category    = category,
                url         = link,
            )
            doc.update(kwargs)
            
            yield doc        
