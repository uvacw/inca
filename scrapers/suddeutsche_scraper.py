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


class suddeutsche(rss):
    """Scrapes sueddeutsche.de """

    def __init__(self):
        self.doctype = "suddeutsche"
        self.rss_url='http://rss.sueddeutsche.de/rss/Topthemen'
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
        req =request.Request("http://rss.sueddeutsche.de/rss/Topthemen")
        read = request.urlopen(req).read()
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
            parag = tree.xpath("//*[@id='article-body']/p//text()")[1:]
            text = ''
            for r in parag:
                text += ' '+r.strip().replace('\xa0',' ')
                #adding a space at the end of the paragraph.
            
            # Retrieving bullet points on top of articles
            try:
                summary = tree.xpath("//*[@id='article-body']/p//text()")[0].strip().replace('\xa0',' ')
            except:
                summary = ''

            bullet = tree.xpath("//*[@id='article-body']/ul//li/text()")
            bullet_text = ''
            for r in bullet:
                bullet_text += ' |||'+r.strip()

            # creating total article_text by merging those two elements.
            article_total = ' '.join(bullet) + ' |||' + text

            # Retrieving the section/category from url
            matchObj = re.match( r'http://www.sueddeutsche.de/(.*?)/', link, re.M|re.I)
            category = matchObj.group(1)

            # Retrieving the byline_source/source from url
            ''' needs to be added '''    
                
            # Retrieving the byline/author
            if tree.xpath("//*[@id='abbr-odg']/text() | //*[@id='abbr-pamu']/text() | //*[@id='abbr-luc']/text()") != []:
                byline_tree = tree.xpath("//*[@id='abbr-odg']/text() | //*[@id='abbr-pamu']/text() | //*[@id='abbr-luc']/text()")[0]
            elif tree.xpath("//*[@class='authorProfileContainer']/span/strong/span/text()") != []:
                byline_tree = tree.xpath("//*[@class='authorProfileContainer']/span/strong/span/text()")
                if len(byline_tree) >1:
                    byline_tree = [x.strip().replace('Gastbeitrag der Schriftstellerin','') for x in byline_tree]
                    byline_tree = ', '.join(byline_tree)
                elif len(byline_tree) == 1:
                    byline_tree = byline_tree[0]
            elif tree.xpath("//*[@class='authorProfileContainer']/span/strong/text()") != []:
                byline_tree = tree.xpath("//*[@class='authorProfileContainer']/span/strong/text()")[0].strip().replace('Gastbeitrag der Schriftstellerin','')
            else:
                byline_tree = ""

            if byline_tree.startswith("Von "):
                byline_tree.replace("Von ","")
            
            # Create iso format date 
            loc= locale.setlocale(locale.LC_ALL, 'de_DE') #first set the date to German.
            xpath_date = tree.xpath("//*[@id='sitecontent']/section[1]/time[@datetime]/text()")[0].strip()
            
            # convert to datetime object
            date= datetime.datetime.strptime(xpath_date, "%d. %B %Y, %H:%M Uhr").isoformat()

            # get title
            title = tree.xpath("(//h1)[1]/text()")

            doc = dict(
                pub_date    = date,
                title       = title[0],
                text        = text,
                bullet      = bullet_text if bullet else '',
                author      = byline_tree,
                # source      = byline_source if byline_source else 'NA',
                category    = category,
                url         = link,
            )
            doc.update(kwargs)
            yield doc
