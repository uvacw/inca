import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class hetlaatstenieuws(rss):
    """Scrapes hln.be"""

    def __init__(self):
        self.doctype = "hetlaatstenieuws (www)"
        self.rss_url= "http://www.hln.be/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=10)

    def parsehtml(self,htmlsource):
        '''                                                                                                                                                                                                                                                                
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                 

        Parameters                                                                                                                                                                                                                                                         
        ----                                                                                                                                                                                                                                                               
        htmlsource: string                                                                                                                                                                                                                                               
            html retrived from RSS feed                                                                                                                                                                                                                                     
            
        yields                                                                                                                                                                                                                                                         
        ----                                                                                                                                                                                                                                                              
        title    the title of the article                                                                                                                                                                                                                                   
        category    sth. like economy, sports, ...                                                                                                                                                                                                                          
        text    the plain text of the article                                                                                                                                                                                                                              
        byline    the author, e.g. "Bob Smith"                                                                                                                                                                                                                             
        byline_source    sth like ANP                                                                                                                                                                                                                                       
        '''
        logging.basicConfig(level=logging.INFO)


        tree = fromstring(htmlsource)

        try:
            typenews = tree.xpath('//*[@class="regio"]//text()')
            # if the news is not regional, then the website has a different layout
            if typenews == [] or typenews =='':
                try:
                    category = tree.xpath('//*[@class="actua_nav"]//text()')[1]
                    #if category == "":
                    #    logger.debug("Could not parse article category?")
                except:
                    category=""
                    logger.debug("Could not parse article category")
                try:
                    byline = tree.xpath('//*[@class="author"]/text()')[0]
                    #if byline == "":
                    #    logger.debug("Could not parse article byline?")
                except:
                    byline=""
                    logger.debug("Could not parse article byline")
                try:
                    bylinesource = tree.xpath('//*[@class="author"]/text()')[1]
                    #if bylinesource == "":
                    #    logger.debug("Could not parse article byline source?")
                except:
                    bylinesource=""
                    logger.debug("Could not parse article byline source")
                try:
                    title = tree.xpath('//*[@id="articleDetailTitle"]/text()')[0]
                except:
                    logger.warning("Could not parse article title")
                    title=""
                subtitle = ""
                try:
                    textfirstpara =" ".join(tree.xpath('//*[@class="intro"]/text() | //*[@class="intro"]/em/text()')).replace("\n","").strip()
                except:
                    logger.debug("Could not parse article teaser")
                    textfirstpara=""
                try:
                    textrest = " ".join(tree.xpath('//*[@class="clear"]/p/text() | //*[@class="clear"]/p/strong/text() | //*[@class="clear"]/p/em/text() | //*[@class="clear"]/h3/text() | //*[@class="clear"]/p/a/text() | //*[@class="clear"]/p/em/text()'))
                except:
                    logger.warning("Could not parse article text")
                    textrest=""
            # for regional news
            else:
                category = 'Regio'
                try:
                    byline = tree.xpath('//*[@class="article__author"]//text()')[0]
                except:
                    byline=""
                    logger.debug("could not parse article category.")
                try:
                    bylinesource = tree.xpath('//*[@class="author"]/text()')[1]
                    #if bylinesource == "":
                    #    logger.info("No bylinesource")
                except:
                    bylinesource=""
                    logger.debug("could not parse article bylinesource")
                try:
                    title = tree.xpath('//*[@itemprop="headline"]/text()')[0]
                except:
                    logger.warning("could not parse article title.")
                    title=""
                try:
                    subtitle = tree.xpath('//*[@class="article__subheader"]/text()')[0]
                except:
                    subtitle = ""
                    logger.debug("could not parse article title.")
                try:
                    textfirstpara =" ".join(tree.xpath('//*[@class="article__intro"]/text()')).replace("\n","").strip()
                except:
                    logger.debug("Could not parse article teaser")
                    textfirstpara=""
                try:
                    textrest = " ".join(tree.xpath('//*[@class="article__body__container"]/h3/text() | //*[@class="article__body__container"]/p/text()')).strip()
                except:
                    logger.warning("Could not parse article text")
                    textrest=""

            texttotal = textfirstpara + " " + textrest
            text = texttotal.replace('(+)','').replace('\xa0','')
            title = title + "\n" + subtitle
            bylinesource2 = "".join(re.findall(r"Bron:(.*)",bylinesource))
            extractedinfo={"title":title.strip(),
                           "category":category.replace("\n","").strip(),
                           "text":text.replace("\n","").strip(),
                           "byline":byline.replace("Door:","").replace("\n"," ").replace("Bewerkt door:","").strip(),
                           "bylinesource":bylinesource2.strip()
                          }
        except:
                #logger.warning('stuff going wrong in het laatste nieuws scraper')
                #print(' DIT MOETEN WE ECHT FIXEN')
                extractedinfo={}

        return extractedinfo
