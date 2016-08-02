import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
        lines = textstring.strip().split('\n')
        lead = lines[0].strip()
        rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
        if rest: result = lead + ' ||| ' + rest
        else: result = lead
        return result.strip()

class nu(rss):
    """Scrapes nu.nl """

    rss_url='http://www.nu.nl/rss'
    doctype = 'nu'
    version = ".1"
    date    = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        tree = fromstring(htmlsource)
        try:
            category = tree.xpath('//*[@class="block breadcrumb "]/div/div/ul/li[2]/a/text()')[0]
            if category == "":
                print("OOps - geen category?")
        except:
            category=""
            print("OOps - geen category?")
        try:
            textfirstpara=tree.xpath('//*[@data-type="article.header"]/div/div[1]/div[2]/text()')[0]
        except:
            print("OOps - geen eerste alinea?")
            textfirstpara=""
        try:
            textrest=tree.xpath('//*[@data-type="article.body"]/div/div/p/text() | //*[@data-type="article.body"]/div/div/p/span/text()| //*[@data-type="article.body"]/div/div/p/em/text() | //*[@data-type="article.body"]/div/div/h2/text() | //*[@data-type="article.body"]/div/div/h3/text() | //*[@data-type="article.body"]/div/div/p/a/em/text() | //*[@data-type="article.body"]/div/div/p/em/a/text() | //*[@data-type="article.body"]/div/div/p/a/text() | //*[@data-type="article.body"]/div/div/p/strong/text()')
            if textrest == "":
                print("OOps - empty textrest for?")
        except:
            print("OOps - geen text?")
            textrest=""
        text = textfirstpara + "\n"+ "\n".join(textrest)
        try:
            #regular author-xpath:
            author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Door:").strip()
            if author_door == "":
                # xpath if link to another hp is embedded in author-info
                try:
                    author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
                except:
                    author_door=""
                    print("OOps - geen author for?")
        except:
            author_door=""
            print("OOps - geen author?")
        author_bron = ""
        text=polish(text)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo



class nos(rss):
    """Scrapes nu.nl """

    rss_url='http://feeds.nos.nl/nosnieuwsalgemeen'
    doctype = 'nos'
    version = ".1"
    date    = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        tree = fromstring(htmlsource)

        try:
            category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/span/a/text()'))
        except:
            category=""
        if category=="":
            try:
                category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/div/div/span/a/text()'))
            except:
                category=""
                print("ooops - geen category")
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()
        except:
            textfirstpara=""
        if textfirstpara=="":
            try:
                textfirstpara=tree.xpath('//*[@id="content"]/article/section/div/div/p/text()')[0]
            except:
                textfirstpara=" "
                print("oops - geen first para")
        try:
            textrest=tree.xpath('//*[@id="content"]/article/section/div/div/p/text() | //*[@id="content"]/article/section/div/div/p/i/text() | //*[@id="content"]/article/section/div/div/p/a/text() | //*[@id="content"]/article/section/div/div/h2/text() | //*[@id="content"]/article/section/div/h2/text() | //*[@id="content"]/article/section/div/div/table/tbody/tr/td/text()')
        except:
            print("oops - geen text?")
            textrest=""
        text ="\n".join(textrest)
        try:
            author_door=tree.xpath('//*[@id="content"]/article/section/div/div/div/span/text()')[0]
        except:
            author_door=""
            print("ooops - geen author")
        author_bron=""
        text=polish(text)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo



            
if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')
