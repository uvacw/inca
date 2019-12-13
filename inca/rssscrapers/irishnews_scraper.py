import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class bbcni(rss):
    """Scrapes imt.ie"""

    def __init__(self):
        self.doctype = "bbc northern ireland (www)"
        self.rss_url = (
            "http://feeds.bbci.co.uk/news/northern_ireland/rss.xml?edition=uk#"
        )
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=4)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                              
        byline_source    sth like ANP                                                                                                                                                                                                                                       
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("cannot parse html tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = " ".join(tree.xpath("//*[@class='story-body__h1']//text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            text = " ".join(tree.xpath("//*[@class='story-body__inner']//p/text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            byline = tree.xpath("//*[@class='byline']//text()")[1]
        except:
            byline = ""
            logger.debug("Could not parse article byline")
        try:
            bylinesource = tree.xpath("//*[@class='byline']//text()")[3]
        except:
            bylinesource = ""
            logger.warning("Could not parse article byline source")

        extractedinfo = {
            "title": title,
            "text": text.replace("\\", ""),
            "byline": byline.strip(),
            "bylinesource": bylinesource,
        }

        return extractedinfo


class herald(rss):
    """Scrapes herald.ie"""

    def __init__(self):
        self.doctype = "herald (www)"
        self.rss_url = "http://www.herald.ie/rss/"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                              
        byline_source    sth like ANP                                                                                                                                                                                                                                       
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse html tree", type(doc), len(doc))
            # print(doc)
            return ("", "", "", "")
        try:
            title = tree.xpath("//*[@id='content']/div[5]/div[1]/article/h1/text()")
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            text = " ".join(tree.xpath("//*[@class='body ']//p//text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            teaser = " ".join(tree.xpath("//*[@class='p']//text()"))
        except:
            teaser = ""
            logger.warning("Could not parse article teaser")
        try:
            byline = " ".join(tree.xpath("//*[@class='byline']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article byline")

        extractedinfo = {
            "title": title,
            "text": text.replace("\\", "").replace("\n", ""),
            "teaser": teaser.replace("\n", ""),
            "byline": byline.strip().replace("\n", ""),
        }

        return extractedinfo


class independent_irl(rss):
    """Scrapes independent.ie"""

    def __init__(self):
        self.doctype = "independent-irl (www)"
        self.rss_url = "http://www.independent.ie/breaking-news/rss/"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=30)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                              
        byline_source    sth like ANP                                                                                                                                                                                                                                       
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("cannot parse html tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = tree.xpath("//*[@id='content']/div[*]/div[1]/article/h1/text()")
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            byline = tree.xpath(
                "//*[@id='content']/div[*]/div[1]/article/section[*]/div[*]/div[*]/div/div[*]/p[*]/a[*]/strong/text()"
            )
        except:
            byline = ""
            logger.debug("Could not parse article byline")
        try:
            text = " ".join(
                tree.xpath("//*[@id='content']/div[*]/div[1]/article//p/text()")
            )
        except:
            text = ""
            logger.warning("Could not parse article text")

        sourcecandidates = "AP|Herald|Press Association"
        lastlines = " ".join(text.split("\n")[-5:])
        bylinesource = " ".join(re.findall(sourcecandidates, lastlines))

        extractedinfo = {
            "title": title,
            "text": text.replace("\\", "").replace("\n", "").strip(),
            "byline": byline,
            "bylinesource": bylinesource,
        }

        return extractedinfo


class irishexaminer(rss):
    """Scrapes irishexaminer.com"""

    def __init__(self):
        self.doctype = "irishexaminer (www)"
        self.rss_url = "http://feeds.examiner.ie/ietopstories"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=30)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        text    the plain text of the article
        teaser    the intro to the artcile                                                                                                                                                                                                                                
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                             
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("cannot parse html tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = tree.xpath("//*[@class='col-left-story']//h1/text()")
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            text = " ".join(tree.xpath("//*[@class='ctx_content']//story/p/text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            teaser = " ".join(tree.xpath("//*[@class='ctx_content']/p//text()"))
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            byline = tree.xpath("//*[@class='byline']//text()")[-1]
        except:
            byline = ""
            logger.debug("Could not parse article byline")

        extractedinfo = {
            "title": title,
            "text": text.strip().replace("\n", ""),
            "teaser": teaser.replace("\xa0", ""),
            "byline": byline.strip(),
        }

        return extractedinfo


class irishtimes(rss):
    """Scrapes irishtimes.com"""

    def __init__(self):
        self.doctype = "irishtimes (www)"
        self.rss_url = "http://www.irishtimes.com/cmlink/news-1.1319192"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=4)

    def get_page_body(self, url):
        """Irish Times has a cookie wall which needs to be bypassed by setting a specific cookie in every request."""
        response = requests.get(url, headers={"Cookie": "cookiewall=yes;"})
        return response.text

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article 
        teaser    the intro to the artcile                                                                                                                                                                                                                                   
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                              
        paywall_na    article behind paywall                                                                                                                                                                                                                                       
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("cannot parse html tree", type(doc), len(doc))
            # logger.warning(doc)
            return ("", "", "", "")
        try:
            title = " ".join(tree.xpath("//*[@property='headline']//text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = " ".join(tree.xpath("//*[@property='description']//text()"))
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            text = " ".join(tree.xpath("//*[@class='article_bodycopy']/p//text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            byline = " ".join(tree.xpath("//*[@class='byline']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article byline")

        paywall = tree.xpath("//*[@class='stub-article-msg']")
        if paywall:
            paywall_na = True
        else:
            paywall_na = False

        extractedinfo = {
            "title": title,
            "teaser": teaser,
            "text": text.strip()
            .replace("\\", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("\r", "")
            .replace("\xa0", ""),
            "byline": byline.replace("\n", ""),
            "paywall_na": paywall_na,
        }

        return extractedinfo


class rte(rss):
    """Scrapes rte.ie"""

    def __init__(self):
        self.doctype = "rte (www)"
        self.rss_url = "https://www.rte.ie/news/rss/news-headlines.xml"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article                                                                                                                                                                                                                                   
        text    the plain text of the article                                                                                                                                                                                                                              
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Cannot parse html tree", type(doc), len(doc))
            # print(doc)
            return ("", "", "", "")
        try:
            title = tree.xpath("//*[@id='main_inner']/header/h1/text()")[0].strip()
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            text = " ".join(tree.xpath("//*[@id='main_inner']//p//text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")

        extractedinfo = {"title": title, "text": text.replace("\xa0", "")}

        return extractedinfo


class thejournal(rss):
    """Scrapes thejournal.ie"""

    def __init__(self):
        self.doctype = "thejournal (www)"
        self.rss_url = "http://www.thejournal.ie/feed/"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=4)

    def parsehtml(self, htmlsource):
        """                                                                                                                                                                                                                                                               
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                               

        Parameters                                                                                                                                                                                                                                                        
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                    
        
        yields                                                                                                                                                                                                                                                              
        ----                                                                                                                                                                                                                                                                
        title    the title of the article
        teaser    the intro to the artcile                                                                                                                                                                                                                                  
        text    the plain text of the article                                                                                                                                                                                                                               
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                              
        """

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("cannot parse html tree", type(htmlsource), len(htmlsource))
            # logger.warning(htmlsource[:100])
            return dict()
        try:
            title = " ".join(tree.xpath("//*[@itemprop='headline']//text()"))
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            teaser = tree.xpath("//*[@itemprop='description']//text()")
        except:
            teaser = ""
            logger.debug("Could not parse article teaser")
        try:
            text = " ".join(tree.xpath("//*[@id='articleContent']//p//text()"))
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            byline = " ".join(tree.xpath("//*[@class='print-author']//text()"))
        except:
            byline = ""
            logger.debug("Could not parse article byline")

        extractedinfo = {
            "title": title,
            "teaser": teaser,
            "text": text,
            "byline": byline.strip(),
        }

        return extractedinfo
