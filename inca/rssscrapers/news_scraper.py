import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
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

class ad(rss):
    """Scrapes ad.nl"""

    def __init__(self):
        self.doctype = "ad (www)"
        self.rss_url='http://www.ad.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        paywall_na    whether the text is behind a paywall
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        paywall = tree.xpath('//*[@class ="fjs-paywall--personal"]')
        if paywall:
            paywall_na = True
        else:
            paywall_na = False
        try:
            title = tree.xpath('//*/h1[@class="article__title"]//text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*/a[@class="sub-nav__link"]//text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        #1. path: regular intro
        #2. path: intro when in <b>; found in a2014 04 130
        teaser=tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro"]//span//text() | //*/p[@class="article__intro"]/span[@class="tag"]//text() | //*/p[@class="article__intro"]//b//text()') [0]
        if teaser=="":
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined); found in 2014 12 1057
        #3. path: second hadings found in 2014 11 1425
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/h2[@class="article__subheader"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
        try:
            author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article author")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
        text=polish(text)

        images = ad._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images,
                       "paywall_na":paywall_na}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     # 'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.ad.nl//cookiewall/accept?url="+link
        return link


class nu(rss):
    """Scrapes nu.nl """

    def __init__(self):
        self.doctype = "nu"
        self.rss_url='http://www.nu.nl/rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        tree = fromstring(htmlsource)
        try:
            category = tree.xpath('//*/li[@class=" active"]/a[@class="trackevent"]//text()')
            if category == "":
                logger.debug("Could not parse article category.")
        except:
            category=""
            logger.debug("Could not parse article category.")
        try:
            teaser=tree.xpath('//*[@class="item-excerpt"]//text()')[0]
        except:
            logger.debug("Could not parse article teaser.")
            teaser=""
        try:
            text=" ".join(tree.xpath('//*[@class="block-wrapper"]/div[@class="block-content"]/p//text()')).strip()
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            #regular author-xpath:
            author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Door:").strip()
            if author_door == "":
                # xpath if link to another hp is embedded in author-info
                try:
                    author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
                except:
                    author_door=""
                    logger.debug("Could not parse article author.")
        except:
            author_door=""
            logger.debug("Could not parse article author.")
        author_bron = ""
        text=polish(text)
        try:
            category = tree.xpath('//*/li[@class=" active"]/a[@class="trackevent"]//text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category.")
        try:
            title = tree.xpath('//h1/text()')[0].strip()
        except:
            title = None
            logger.warning("Could not parse article title.")

        images = nu._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}
        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//div[@class="item-image"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

class nos(rss):
    """Scrapes nos.nl """
    def __init__(self):
        self.doctype = "nos (www)"
        self.rss_url='http://feeds.nos.nl/nosnieuwsalgemeen'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.error("HTML tree cannot be parsed")
        try:
            title = tree.xpath('//h1')[0].text
        except:
            title = ""
            logger.warning("Could not parse article title")
        try:
            category="".join(tree.xpath('//*/a[@id="link-grey"]//text()'))
        except:
            category=""
            logger.debug("Could not parse article title")
        if category=="":
            try:
                category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/div/div/span/a/text()'))
            except:
                category=""
                logger.debug("Could not parse article category")
        try:
            teaser=tree.xpath('//*[@class="article_textwrap"]/p/em//text()')[0]
        except:
            logger.debug("Could not parse article teaser")
            teaser=""
        try:
            text=" ".join(tree.xpath('//*[@class="article_textwrap"]/p//text()')).strip()
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            author_door=tree.xpath('//*[@id="content"]/article/section/div/div/div/span/text()')[0]
        except:
            author_door=""
            logger.debug("Could not parse article source")
        author_bron=""
        text=polish(text)

        images = nos._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images
                       }

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            try:
                img = element.xpath('//figure[@class="article_head_image block_largecenter"]//img')[0]
                image = {'url' : img.attrib['src'],
                 #'height' : img.attrib['height'],
                 #'width' : img.attrib['width'],
                 #'caption' : element.xpath(element.xpath('.//div[@Class="caption_content"]/text()')),
                 'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            except IndexError:
                pass
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        # link=re.sub("/$","",link)
        # link="http://www.nos.nl//cookiesv2.publiekeomroep.nl/consent/all"+link
        # currently, there is no cookiewall in place, so we just return the link as it is
        return link

class volkskrant(rss):
    """Scrapes volkskrant.nl """

    def __init__(self):
        self.doctype = "volkskrant (www)"
        self.rss_url='http://www.volkskrant.nl/nieuws/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)


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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        paywall_na    whether the text is behind a paywall
        '''


        tree = fromstring(htmlsource)
        paywall = tree.xpath('//*[@class ="fjs-paywall--personal"]')
        if paywall:
            paywall_na = True
        else:
            paywall_na = False
        try:
            title = tree.xpath('//*/h1[@class="artstyle__header-title artstyle__header-title--white artstyle__header-title--light"]//text() | //*/h1[@class="artstyle__header-title"]//text() | //*/h1[@class="artstyle__header-title artstyle__header-title--white"]//text() | //*[@class="artstyle__header-title artstyle__header-title--hero-bleed artstyle__header-title--light"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category=tree.xpath('//*/span[@class="artstyle__labels__section"]//text()')[0]
        except:
            category=""
        if category=="":
            try:
                category=tree.xpath('//*[@class="action-bar__primary"]/a/text()')[0]
            except:
                category=""
                logger.debug("Could not parse article category")
        try:
            teaser=tree.xpath('//*/p[@class="artstyle__intro artstyle__intro--center"]//text() | //*/p[@class="artstyle__intro artstyle__intro--center"]/span//text() | //*/p[@class="artstyle__intro artstyle__intro--center"]/a//text() | //*/p[@class="artstyle__intro"]//text() | //*/p[@class="artstyle__intro"]//text()')[0]
        except:
            logger.debug("Could not parse article teaser")
            teaser=""
        try:
            #1. path: regular textrest
            #2. path: textrest version found in 2014 11 16
            #3. path: second heading found in 2014 11 50
            #4. path: text with link behind; found in 2014 10 2455(html-file-nr)
            #5. path: old design regular text
            #6. path: old design second heading
            #7. path:old design text with link
            textrest=tree.xpath('//*/p[@class="artstyle__text artstyle__text--drop-cap"]//text() | //*/p[@class="artstyle__text"]//text() | //*/h3[@class="artstyle__title"]//text()')
        except:
            logger.warning("Could not parse article text")
            textrest=""
        text = "\n".join(textrest)
        try:
            author_door=tree.xpath('//*/a[@class="artstyle__byline__author"]/text()')[0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door=" ".join(tree.xpath('//*[@class="article__meta--v2"]/span/span[2]/text()')).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:")
            except:
                logger.debug("Could not parse article author")
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
                    logger.debug("Could not parse article byline source")
        if author_door=="" and author_bron=="" and category=="Opinie":
            author_door = "OPINION PIECE OTHER AUTHOR"
        text=polish(text)

        images = volkskrant._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images,
                       "paywall_na":paywall_na}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article-photo fjs-gallery-item"]//img | //figure[@class="top-media--back fjs-gallery-item"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))}
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.volkskrant.nl//cookiewall/accept?url="+link
        return link


class nrc(rss):
    """Scrapes nrc.nl """
    def __init__(self):
        self.doctype = "nrc (www)"
        self.rss_url='http://www.nrc.nl/rss.php?n=np'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=9, day=10)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        tree=fromstring(htmlsource)

        try:
            title = tree.xpath('//*[@class="center-block intro-col article__header"]/h1/text() | //*[@class="liveblog__header__inner"]/h1/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*[@id="broodtekst"]/a[1]/text() | //*[@class="article__flag"]//text() | //*[@class="keyword"]//text()')[0]
        except:
            category = ""
            logger.debug("Could not parse article category")
        if category=="":
            try:
                category=tree.xpath('//*[@class="article__section-branding"]/text()')[0]
            except:
                category=""
        try:
            teaser=tree.xpath('//*[@class="intro article__intro"]/p//text() | //*[@class="intro article__intro"]//text()')[0]
        except:
            logger.info("OOps - geen eerste alinea?")
            teaser=""
        text=" ".join(tree.xpath('//*[@class="content article__content"]/p//text() | //*[@class="content article__content"]/h2//text()')).strip()
        if text=="":
            logger.warning("Could not parse article text")
        textnew=re.sub("Follow @nrc_opinie","",text)
        try:
            author_door = tree.xpath('//*[@class="author"]/span/a/text()')[0]
        except:
            author_door = ""
        if author_door == "":
            try:
                author_door = tree.xpath('//*[@class="auteur"]/span/a/text()')[0]
            except:
                author_door = ""
        if author_door == "":
            try:
                author_door = tree.xpath('//*[@class="authors"]/ul/li/text()')[0]
            except:
                author_door = ""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__byline__author-and-date"]/a/text()')[0]
            except:
                author_door = ""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="content article__content"]/span[@class="byline"]//text()')[0]
            except:
                author_door = ""
        author_bron=""
        if textnew=="" and category=="" and author_door=="":
            logger.debug("No article-page?")
            try:
                if tree.xpath('//*[@class="kies show clearfix"]/h2/text()')[0] == 'Lees dit hele artikel':
                    text="THIS SEEMS TO BE AN ARTICLE ONLY FOR SUBSCRIBERS"
                    logger.warning("This seems to be a subscribers-only article")
            except:
                    text=""
                    logger.warning("Could not parse article text")
        text=polish(text)

        images = nrc._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="responsive-img-div img-b1bc3f75894aebe980b93536058622c9  loaded"]//img | //*[@class="responsive-img-div__click-catcher"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))}
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

class parool(rss):
    """Scrapes parool.nl """
    def __init__(self):
        self.doctype = "parool (www)"
        self.rss_url='http://www.parool.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

    def parseurl(self,url):
        link = url.lstrip('http://www.parool.nl///cookiewall/accept?url=')
        try:
            category=re.findall("/+[a-z]+/", link)[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        if category=="":
            try:
                category=re.findall("/+[a-z]+-+[a-z]+-+[a-z]+/", link)[0]
            except:
                category=""
                logger.debug("Could not parse article category")
        category = category.replace("/","")
        return {'category':category}

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        paywall_na    whether the text is behind a paywall
        '''

        tree = fromstring(htmlsource)
        paywall = tree.xpath('//*[@class ="fjs-paywall--personal"]')
        if paywall:
            paywall_na = True
        else:
            paywall_na = False
        try:
            title = tree.xpath('//*/h1[@class="article__title"]//text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
            category=""
        try:
            teaser = tree.xpath('//*/p[@class="article__intro"]')[0].text_content().strip()
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        text=" ".join(tree.xpath('//*/p[@class="article__body__paragraph first"]//text() | //*/p[@class="article__body__paragraph"]//text() | //*/h2[@class="article__body__title"]//text()')).strip()
        author_text=tree.xpath('//*[@class=" article__author"]//text()')
        try:
            author_door=[e for e in author_text if e.find("Door")>=0][0].strip().replace("(","").replace(")","").replace("Door:","")
        except:
            author_door=""
        if author_door=="":
            try:
                author_door=[e for e in author_text if e.find("Bewerkt door:")>=0][0].strip().replace("(","").replace(")","").replace("Bewerkt door:","")
            except:
                author_door=""
                logger.debug("Could not parse article author")
        try:
            bron_text=tree.xpath('//*[@id="page-main-content"]//*[@class="article__footer"]/span/span/text()')[0]
            author_bron=re.findall(".*?Bron:(.*)", bron_text)[0]
        except:
            author_bron=" "
        if author_bron=="":
            try:
                bron_text=tree.xpath('//*/span[@class="author-info__source"]/text()')[0]
                author_bron=re.findall(".*?Bron:(.*)",bron_text)[0]
            except:
                author_bron=""
                logger.debug("Could not parse byline source")
        text=polish(text)

        images = parool._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "teaser":teaser,
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images,
                       "paywall_na":paywall_na}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article-photo fjs-gallery-item"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))}
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.parool.nl///cookiewall/accept?url="+link
        return link


class trouw(rss):
    """Scrapes trouw.nl """
    def __init__(self):
        self.doctype = "trouw (www)"
        self.rss_url='http://www.trouw.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)


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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        paywall_na    whether the text is behind a paywall
        '''

        tree = fromstring(htmlsource)
        paywall = tree.xpath('//*[@class ="paywall-notice__body"]')
        if paywall:
            paywall_na = True
        else:
            paywall_na = False
        try:
            title = tree.xpath('//*/h1[@class="article__header__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            teaser = tree.xpath('//*/p[@class="article__introduction__text"]//text() | //*/section[@class="article__introduction layout__stage--center"]//text()')[0]
        except:
            teaser=" "
            logger.debug("Could not parse article teaser")
        try:
            category=tree.xpath('//*[@id="subnav_nieuws"]/li/a/span/text() | //*/a[@class="article__header__meta__section-link"]//text()')[0]
        except:
            category=""
        if category=="":
            try:
                category=tree.xpath('//*[@id="str_cntr2"]//*[@class="dos_default dos_film"]/h2/text()')[0]
            except:
                category=""
        if category=="":
            try:
                category=tree.xpath('//*[@id="str_cntr2"]//*[@class="dos_default dos_vluchtelingen"]/span/text()')[0]
            except:
                category=""
                logger.debug("Could not parse article category")
        try:
        #1. Regular text - intro
        #2. Bold text - subtitles
        #3. Regular  text
        #4. Extra box title
        #5. Extra box text
        #6. Link text
        #7. Explanantion box text
        #8. italics
            textrest=tree.xpath('//*[@class="article__section-title__text heading-3"]/text() | //*/p[@class="article__paragraph"]//text() | //*/figcaption[@class="article__photo__caption"]//text() | //*[@class="article__paragraph"]/text() | //*[@class="article__quote__text"]/text() | //*[@class="article__framed-text__title"]/text() | //*[@id="art_box2"]/section/p/text() |  //*[@id="art_box2"]/p/a/text() |  //*[@id="art_box2"]//*[@class="embedded-context embedded-context--inzet"]/text() |  //*[@id="art_box2"]/p/em/text()')
        except:
            textrest=" "
            logger.warning("Could not parse article text")
        text = "\n".join(textrest)
        try:
             author_door=tree.xpath('//*[@class="author"]/text() | //*/strong[@class="article__header__meta__author"]/text()')[0]
        except:
             author_door=" "
             logger.debug("Could not parse article author")
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
                    logger.debug("Could not parse byline source")

        text=polish(text)

        images = trouw._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images,
                       "paywall_na":paywall_na}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__cover layout__stage--center"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))}
                     # 'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.trouw.nl/cookiewall/accept?url="+link
        return link

class telegraaf(rss):
    """Scrapes telegraaf.nl """
    def __init__(self):
        self.doctype = "telegraaf (www)"
        self.rss_url='http://www.telegraaf.nl/rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        paywall_na    whether the text is behind a paywall
        '''


        tree = fromstring(htmlsource)
        paywall = tree.xpath('//*[@class ="bg-premium all-paddings-6"]')
        if paywall:
            paywall_na = True
        else:
            paywall_na = False
        try:
            title = tree.xpath('//*/h1[@class="article-title playfair-bold-l no-top-margin no-bottom-margin gray1"]/text()|//*/h1[@class="article-title playfair-bold-l playfair-bold-xl--m playfair-bold-g--l no-top-margin no-bottom-margin gray1"]/text()|//*/h2[@class="ui-tab-gothic-bold ui-text-medium"]/text() | //*/h1[@class="ui-stilson-bold ui-text-large ui-break-words ui-dark3 ui-no-top-margin ui-bottom-margin-2 ui-top-padding-2"]/text()|//*/h2[@class="no-top-margin bottom-margin-3 bottom-margin-4--l roboto-black-l roboto-black-xl--l gray2"]/text()') [0] 
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*/a[@class="inline-block gray1 roboto-black-s uppercase-text no-underline bottom-padding-1 bottom-border-thin"]/text()' )[0]
        except:
            category = ""
            logger.debug("Could not parse article category")
        try:
            teaser=tree.xpath('//*/p[@class="abril-bold no-top-margin"]//text()')[0]
        except:
            logger.debug("Could not parse article teaser")
            teaser=""
        try:
            text=" ".join(tree.xpath('//*/p[@class="false bottom-margin-6"]//text() | //*/p[@class="false bottom-margin-6"]/span[class="bold"]//text()')).strip()
        except:
            text = ""
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*[@class="auteur"]/text() | //*[@class="ui-table ui-gray3"]/span[2]/text()')[0].strip().lstrip("Van ").lstrip("onze").lstrip("door").strip()
        except:
            author_door = ""
            logger.debug("Could not parse article source")
        author_bron=""
        text=polish(text)

        images = telegraaf._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images,
                       "paywall_na":paywall_na}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="__picture picture height-100 absolute top-left-corner width-100 no-borders"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : self.rss_url[:-4] + img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']
                }
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images



class metro(rss):
    """Scrapes metronieuws.nl """

    def __init__(self):
        self.doctype = "metro (www)"
        self.rss_url='http://www.metronieuws.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
        image: images included in the article
        '''


        tree = fromstring(htmlsource)
        try:
            title = tree.xpath('//*[@class="row"]/h1/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*[@class="active"]/text() | //*/a[@title class="active"]/text()')[0]
        except:
            category = ""
            logger.debug("Could not parse article category")
    #fix: xpath for category in new layout leads to a sentence in old layout:
        if len(category.split(" ")) >1:
            category=""
        try:
        #1. path: regular text
        #2. path: text with link behind, fi 2014 12 646
        #3. path: italic text, fi 2014 12 259
        #4. path: second headings, fi 2014 12 222
        #5. path: another version of regualr formated text, fi 2014 12 1558
        #6. path: another version a second heading, fi 2014 12 1923
        #7. path: italic text with link behind in span environment, fi 2014 11 540
        #8. path: italic text with link behind, not in span evir, fi 2014 10 430
        #--until here code is just copied from spits
        #10. path: bold and italic text, fi 2014 12 04
        #11. path: bold text, fi 2014 12 04
        #12. path: second headings
        #13. path: regular text
            textrest=tree.xpath('//*[@class="field-item even"]/p/text() | //*[@class="field-item even"]/p/a/text() | //*[@class="field-item even"]/p/em/text() | //*[@class="field-item even"]/h2/text() | //*[@class="field-item even"]/p/span/text() | //*[@class="field-item even"]/h2/span/text() | //*[@class="field-item even"]/p/span/em/a/text() | //*[@class="field-item even"]/p/em/a/text() | //*[@class="field-item even"]/p/em/strong/text() | //*[@class="field-item even"]/p/b/text() | //*[@class="field-item even"]/div/text() | //*[@class="field-item even"]/p/strong/text()')
        except:
            logger.debug("Could not parse article text")
            textrest = ""
        text = "\n".join(textrest)
        text=re.sub("Lees ook:"," ",text)
        try:
        #new layout author:
            author_door = tree.xpath('//*[@class="username"]/text()')[0].strip().lstrip("door ").lstrip("© ").lstrip("2014 ").strip()
        except:
            author_door = ""
            logger.debug("Could not parse article source")
        if author_door=="":
        #try old layout author
            try:
                author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
            except:
                author_door = ""
        author_bron=""
        text=polish(text)

        images = metronieuws._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="image row"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

class geenstijl(rss):
    """Scrapes geenstijl.nl """

    def __init__(self):
        self.doctype = "geenstijl"
        self.rss_url='https://www.geenstijl.nl/feeds/recent.atom'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=9, day=15)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        '''


        tree = fromstring(htmlsource)
        textrest=tree.xpath('//*[@class="article_content"]/p//text() | //*[@class="article_content"]/p/strong//text() | //*[@class="article_content"]/p/em//text() | //*/h2[@class="content-title"]//text()')
        if textrest=="":
            logger.warning("Could not parse article text")
        text="\n".join(textrest)
        try:
            title = tree.xpath('//*[@class="col-xs-12"]/h1/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            teaser=tree.xpath('//*[@class="article-intro"]/p/text()')[0]
        except:
            teaser=""
            logger.warning("Could not parse article teaser")
        try:
            author_door=tree.xpath('//*[@class="col-xs-12 col-sm-7"]/a[@rel="author"]//text()')[0].replace("|","")
        except:
            author_door=""
            logger.warning("Could not parse article source")

        text=polish(text)

        images = geenstijl._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "teaser": teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="article_img_container"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="https://www.geenstijl.nl%2Fsetcookie.php?t="+link
        return link

class fok(rss):
    """Scrapes fok.nl """

    def __init__(self):
        self.doctype = "fok"
        self.rss_url='http://rss.fok.nl/feeds/nieuws'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)


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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        tree = fromstring(htmlsource)
        try:
            title = tree.xpath('//*/header[@class="hasHidden"]/h1/text()')
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            teaser=tree.xpath('//*/article[@class="single"]/p[0]//text()')
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        try:
            category="".join(tree.xpath('//*[@id="crumbs"]/ul/li/a/text()'))
        except:
            category = ""
            logger.category("Could not parse article category")
        if len(category.split(" ")) >1:
            category=""
        try:
            textrest=tree.xpath('//*/article[@class="single"]/p//text() | //*/article[@class="single"]/p/em//text() | //*[@role="main"]/article/p//text() | //*[@role="main"]/article/p/strong//text() | //*[@role="main"]/article/p/strong/a//text() | //*[@role="main"]/article/p/a//text() | //*[@role="main"]/article/p/em//text() | //*[@id="mainContent"]//*[@role="main"]/article/p//text() | //*[@id="mainContent"]/div[5]/main/article/p//text()')
        except:
            print("geen text")
            logger.warning("Could not parse article text")
            textrest = ""
        text = "\n".join(textrest)
        try:
             author_door = tree.xpath('//*[@class="mainFont"]/text()')[0].strip()
        except:
            author_door = ""
            logger.debug("Could not parse article source")
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
            except:
                author_door = ""
        try:
            author_bron=tree.xpath('//*[@class="bron"]/strong/text()')[0]
        except:
            author_bron=""
        if author_bron=="":
            try:
                author_bron=tree.xpath('//*[@class="bron"]/strong/a/text()')[0]
            except:
                author_bron=""
                logger.debug("Could not parse article source byline")
        textnew=polish(textnew)

        images = fok._extract_images(self,tree)

        extractedinfo={"title":title,
                       "category":category.strip(),
                       "teaser":teaser,
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="col-4 first"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images


if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')


class destentor(rss):
    """Scrapes destentor.nl"""

    def __init__(self):
        self.doctype = "destentor (www)"
        self.rss_url="http://www.destentor.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=3)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
    #        teaser = tree.xpath('//*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/span/text() |  //*/p[@class="article__intro"]/span/b/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text

        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()

        # text = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/b/text() | //*/time[@class="liveblog__time-text"]/text() | //*/p[@class="liveblog__intro"]/text() | //*/p[@class="liveblog__paragraph"]/text() | //*/p[@class="liveblog__paragraph"]/strong/text() | //*/p[@class="liveblog__paragraph"]/a/text()')
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
            logger.debug("Could not parse article source")
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        images = destentor._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     # 'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.destentor.nl///cookiewall/accept?url="+link
        return link

# Local newspapers

class bd(rss):
    """Scrapes bd.nl"""

    def __init__(self):
        self.doctype = "bd (www)"
        self.rss_url="http://www.bd.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=9)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/span[@class="article__source"]/span/text()| //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article author")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article source byline")

        # text=polish(text)

        images = bd._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images
                       }

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.bd.nl///cookiewall/accept?url="+link
        return link

class gelderlander(rss):
    """Scrapes gelderlander.nl"""

    def __init__(self):
        self.doctype = "gelderlander (www)"
        self.rss_url="http://www.gelderlander.nl/home/rss.xml"
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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        #text = tree.xpath('//*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/h2[@class="article__subheader"]/text() | //*/p[@class="article__paragraph"]/b/text() | //*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/i/text() | //*/p[@class="article__paragraph"]/a/i/text()')
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article byline source")

        # text=polish(text)

        images = gelderlander._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.gelderlander.nl///cookiewall/accept?url="+link
        return link

class ed(rss):
    """Scrapes ed.nl"""

    def __init__(self):
        self.doctype = "ed (www)"
        self.rss_url="http://www.ed.nl/home/rss.xml"
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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        # text = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/b/text() | //*/time[@class="liveblog__time-text"]/text() | //*/p[@class="liveblog__intro"]/text() | //*/p[@class="liveblog__paragraph"]/text() | //*/p[@class="liveblog__paragraph"]/strong/text() | //*/p[@class="liveblog__paragraph"]/a/text()')
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article source byline")

        # text=polish(text)

        images = ed._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images


    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.ed.nl///cookiewall/accept?url="+link
        return link

class bndestem(rss):
    """Scrapes bndestem.nl"""

    def __init__(self):
        self.doctype = "bndestem (www)"
        self.rss_url="http://www.bndestem.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        # 1. path = normal intro
        # 2. path = normal intro version 2
        # 3. path = normal intro version 3
        # 4. path = bold intro
        # 5. path = bold intro version 2
        # 6. path = intro video
        # 7. path = intro video version 2
        # 8. path = links in intro video
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() |  //*/p[@class="article__intro"]/span/b/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: bold paragraph headings - version 2
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        # text = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/h2[@class="article__subheader"]/text() | //*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/b/text() | //*/p[@class="article__paragraph"]/i/text() | //*[@class="s-element-content s-text emojify"]/text() | //*[@class="s-element-content s-text emojify"]/b/text() | //*[@class="s-element-content s-text emojify"]/u/text() | //*[@class="s-element-content s-text emojify"]/u/b/text() | //*[@class="s-element-content s-text emojify"]/a/text() | //*[@class="s-element-content s-text emojify"]/b/a/text()')
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article source byline")


        # text=polish(text)

        images = bndestem._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.bndestem.nl///cookiewall/accept?url="+link
        return link

class pzc(rss):
    """Scrapes pzc.nl"""

    def __init__(self):
        self.doctype = "pzc (www)"
        self.rss_url="http://www.pzc.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        # 1. path = normal intro
        # 2. path = normal intro version 2
        # 3. path = normal intro version 3
        # 4. path = bold intro
        # 5. path = bold intro version 2
        # 6. path = intro video
        # 7. path = intro video version 2
        # 8. path = links in intro video
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() |  //*/p[@class="article__intro"]/span/b/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text
       # text = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/b/text() | //*/time[@class="liveblog__time-text"]/text() | //*/p[@class="liveblog__intro"]/text() | //*/p[@class="liveblog__paragraph"]/text() | //*/p[@class="liveblog__paragraph"]/strong/text() | //*/p[@class="liveblog__paragraph"]/a/text()')
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article source byline")

        # text=polish(text)

        images = pzc._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images


    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.pzc.nl///cookiewall/accept?url="+link
        return link

class tubantia(rss):
    """Scrapes tubantia.nl"""

    def __init__(self):
        self.doctype = "tubantia (www)"
        self.rss_url="http://www.tubantia.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        # 1. path = normal intro
        # 2. path = normal intro version 2
        # 3. path = normal intro version 3
        # 4. path = bold intro
        # 5. path = bold intro version 2
        # 6. path = intro video
        # 7. path = intro video version 2
        # 8. path = links in intro video
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() |  //*/p[@class="article__intro"]/span/b/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        # text = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/b/text() | //*/time[@class="liveblog__time-text"]/text() | //*/p[@class="liveblog__intro"]/text() | //*/p[@class="liveblog__paragraph"]/text() | //*/p[@class="liveblog__paragraph"]/strong/text() | //*/p[@class="liveblog__paragraph"]/a/text()')
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article source byline")

        # text=polish(text)

        images = tubantia._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__figure"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images


    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.tubantia.nl///cookiewall/accept?url="+link
        return link

class limburger(rss):
    """Scrapes limburger.nl"""

    def __init__(self):
        self.doctype = "limburger (www)"
        self.rss_url="http://feeds.feedburner.com/Limburgernl-nieuws?format=xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@itemprop="name"]/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        # 1. path = normal intro
        # 2. path = normal intro version 2
        # 3. path = normal intro version 3
        # 4. path = bold intro
        # 5. path = bold intro version 2
        # 6. path = intro video
        # 7. path = intro video version 2
        # 8. path = links in intro video
        try:
            teaser=" ".join(tree.xpath('//*[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() |  //*/p[@class="article__intro"]/span/b/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        #2. path: text with link behind (shown in blue underlined);
        #3. path: second headings
        #4. path: span paragraphs
        #5. path: bold paragraph headings
        #6. path: live blogs time
        #7. path: live blogs intro or heading
        #8. path: live blogs body text
        #9. path: live blogs strong body text
        #10. path: live blogs link body text
        text=" ".join(tree.xpath('//*[@class="article__body"]/p//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        # text = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/b/text() | //*/time[@class="liveblog__time-text"]/text() | //*/p[@class="liveblog__intro"]/text() | //*/p[@class="liveblog__paragraph"]/text() | //*/p[@class="liveblog__paragraph"]/strong/text() | //*/p[@class="liveblog__paragraph"]/a/text()')
        if text=="":
            logger.warning("Could not parse article text")
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article byline source")

        # text=polish(text)

        images = limburger._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//figure[@class="article__image"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src'],
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

        return extractedinfo

class frieschdagblad(rss):
    """Scrapes frieschdagblad.nl"""

    def __init__(self):
        self.doctype = "frieschdagblad (www)"
        self.rss_url="http://www.frieschdagblad.nl/nieuws.asp"
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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*[@class="ArtKopStd"]/b/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
            category = tree.xpath('//*/span[@class="rubriek"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        #no teaser
        try:
            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        text = tree.xpath('//*[@class="ArtTekstStd"]/text()')
        if text=="":
            logger.warning("Could not parse article text")
        #no author
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article byline_source")

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text,
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo

class zwartewaterkrant(rss):
    """Scrapes zwartewaterkrant.nl"""

    def __init__(self):
        self.doctype = "zwartewaterkrant (www)"
        self.rss_url="http://www.zwartewaterkrant.nl/rss.php"
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
        teaser    the intro to the artcile 
        text    the plain text of the article
        byline    the author, e.g. "Bob Smith"
        byline_source    sth like ANP
        image: images included in the article
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("Could not parse HTML tree",type(doc),len(doc))
            #print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*[@id="containerContent"]/h2/text()')[0]
        except:
            title=""
            logger.warning("Could not parse article title")
        try:
        # 1. path = normal articles
            category = tree.xpath('//*/span[@class="rubriek"]/text()')[0]
        except:
            category=""
            logger.debug("Could not parse article category")
        try:
            teaser=tree.xpath('//*/span[@class="blackbold"]/text()')[0]
        except:
            teaser=""
            logger.debug("Could not parse article teaser")
        #1. path: regular text
        text = tree.xpath('//*[@id="containerContent"]/p/text() | //*[@id="containerContent"]/p/a/text()')
        if text=="":
            logger.warning("Could not parse article text")
        #no author
        try:
            author_door = tree.xpath('//*/span[@class="article__source"]/b/text() | //*/p[@class="article__paragraph"]/b/i/text()') [0]
        except:
            author_door=""
        if author_door=="":
            try:
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door==""
        if author_door=="":
            try:
                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                logger.debug("Could not parse article source")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
            logger.debug("Could not parse article byline source")

        # text=polish(text)

        images = zwartewaterkrant._extract_images(self,tree)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text,
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="containerContent"]//img')
            if len(img_list)>0:
                img = img_list[0]
                image = {'url' : img.attrib['src']}
                     #'height' : img.attrib['height'],
                     #'width' : img.attrib['width'],
                     #'caption' : _fon(element.xpath('.//p[@Class="imageCaption"]/text()'))
                     #'alt' : img.attrib['alt']}
                if image['url'] not in [i['url'] for i in images]:
                    images.append(image)
            else:
                images=[]
        return images

        return extractedinfo
