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
    """Scrapes nos.nl """

    rss_url='http://feeds.nos.nl/nosnieuwsalgemeen'
    doctype = 'nos (www)'
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


class volkskrant(rss):
    """Scrapes volkskrant.nl """

    rss_url='http://www.volkskrant.nl/nieuws/rss.xml'
    doctype = 'volkskrant (www)'
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
            category=tree.xpath('//*[@class="action-bar__primary"]/div/a/text()')[0]
        except:
            category=""
        if category=="":
            try:
                category=tree.xpath('//*[@class="action-bar__primary"]/a/text()')[0]
            except:
                category=""
                print("oops - geen category")
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()
        except:
            textfirstpara=""
        if textfirstpara=="":
            try:
                textfirstpara=tree.xpath('//*/header/p/text()')[1].replace("\n", "").strip()
            except:
                textfirstpara=" "
                print("oops - geen first para")
        try:
            #1. path: regular textrest
            #2. path: textrest version found in 2014 11 16
            #3. path: second heading found in 2014 11 50
            #4. path: text with link behind; found in 2014 10 2455(html-file-nr)
            #5. path: old design regular text
            #6. path: old design second heading
            #7. path:old design text with link
            textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() | //*[@class="article__body__container"]/p[*]/text() | //*[@class="article__body__container"]/h3/text() | //*[@class="article__body__container"]/p/a/text() | //*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/p/strong/text() | //*[@id="art_box2"]/p/a/text() | //*/p[@class="article__body__paragraph first"]/text() | //*/div[@class="article__body"]/h2/text() | //*/p[@class="article__body__paragraph first"]/a/text() | //*/p[@class="article__body__paragraph"]/text() | //*/h3[@class="article__body__container-title"]/text()')
            #print("Text rest: ")
            #print(textrest)
        except:
            print("oops - geen text?")
            textrest=""
        text = textfirstpara + "\n"+ "\n".join(textrest)
        try:
            author_door=" ".join(tree.xpath('//*/span[@class="author"]/*/text() | //*/span[@class="article__body__container"]/p/sub/strong/text() |//*/span[@class="article__author"]/text()' )).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
            # geeft het eerste veld: "Bewerkt \ door: Redactie"
            if author_door=="edactie":
                author_door = "redactie"
        except:
            author_door=""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
                if author_door=="edactie":
                    author_door = "redactie"
            except:
                author_door=""
                print("oops - geen auhtor?")
        try:
            author_bron=" ".join(tree.xpath('//*/span[@class="article__meta"][*]/text()')).strip().lstrip("Bron:").strip()
            # geeft het tweede veld: "Bron: ANP"
        except:
            author_bron=""
        if author_bron=="":
            try:
                author_bron=" ".join(tree.xpath('//*/span[@class="author-info__source"]/text()')).strip().lstrip("- ").lstrip("Bron: ").strip()
            except:
                author_bron=""
        if author_bron=="":
            try:
                bron_text=tree.xpath('//*[@class="time_post"]/text()')[1].replace("\n", "")
                author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
            except:
                author_bron=""
            if author_bron=="":
                try:
                    bron_text=tree.xpath('//*[@class="time_post"]/text()')[0].replace("\n", "")
                    author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
                except:
                    author_bron=""
            if author_bron=="":
                try:
                    bron_text=tree.xpath('//*[@class="article__meta--v2"]/span/text()')[0].replace("\n","")
                    author_bron=re.findall(".*?Bron:(.*)", bron_text)[0]
                except:
                    author_bron=""
                    print("oops - geen bron")
        if author_door=="" and author_bron=="" and category=="Opinie":
            author_door = "OPINION PIECE OTHER AUTHOR"
        text=polish(text)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.volkskrant.nl//cookiewall/accept?url="+link
        return link


            
if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')
