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

class ad(rss):
    """Scrapes ad.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "ad (www)"
        self.rss_url='http://www.ad.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        #1. path: regular intro                                                                                                    
        #2. path: intro when in <b>; found in a2014 04 130                                                                         
        textfirstpara=tree.xpath('//*[@id="detail_content"]/p/text() | //*[@class="intro"]/b/text() | //*[@class="intro"]/span/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text()')
        if textfirstpara=="":
            logger.info("OOps - geen eerste alinea?")
        #1. path: regular text                                                                                                     
        #2. path: text with link behind (shown in blue underlined); found in 2014 12 1057                                          
        #3. path: second hadings found in 2014 11 1425   
        textrest = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*[@class="article__paragraph"]/span/text() | //*[@id="detail_content"]/section/p/a/text() | //*[@id="detail_content"]/section/p/strong/text() | //*/p[@class="article__paragraph"]/strong/text()')
        if textrest=="":
            logger.info("OOps - empty textrest")
        text = "\n".join(textfirstpara) + "\n" + "\n".join(textrest)
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""
        text=polish(text)

        images = ad._extract_images(self,tree)

        extractedinfo={"text":text.strip(),
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
        link="http://www.ad.nl//cookiewall/accept?url="+link
        return link

    
class nu(rss):
    """Scrapes nu.nl """

    def __init__(self,database=True):
        self.database=database
        self.doctype = "nu"
        self.rss_url='http://www.nu.nl/rss'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
                logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            textfirstpara=tree.xpath('//*[@data-type="article.header"]/div/div[1]/div[2]/text()')[0]
        except:
            logger.info("OOps - geen eerste alinea?")
            textfirstpara=""
        try:
            textrest=tree.xpath('//*[@data-type="article.body"]/div/div/p/text() | //*[@data-type="article.body"]/div/div/p/span/text()| //*[@data-type="article.body"]/div/div/p/em/text() | //*[@data-type="article.body"]/div/div/h2/text() | //*[@data-type="article.body"]/div/div/h3/text() | //*[@data-type="article.body"]/div/div/p/a/em/text() | //*[@data-type="article.body"]/div/div/p/em/a/text() | //*[@data-type="article.body"]/div/div/p/a/text() | //*[@data-type="article.body"]/div/div/p/strong/text()')
            if textrest == "":
                logger.info("OOps - empty textrest for?")
        except:
            logger.info("OOps - geen text?")
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
                    logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        except:
            author_door=""
            logger.info("No 'author' field encountered - don't worry, maybe it just doesn't exist.")
        author_bron = ""
        text=polish(text)
        try:
            category = tree.xpath('//*[@class="container"]/h1/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")

        try:
            title = tree.xpath('//h1/text()')[0].strip()
        except:
            title = None
            logger.warning("No title encountered")

        images = nu._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "title":title,
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
    def __init__(self,database=True):
        self.database = database
        self.doctype = "nos (www)"
        self.rss_url='http://feeds.nos.nl/nosnieuwsalgemeen'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try: 
            tree = fromstring(htmlsource)
        except:
            logger.error("HTML tree cannot be parsed")
        try:
            category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/span/a/text()'))
        except:
            category=""
        if category=="":
            try:
                category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/div/div/span/a/text()'))
            except:
                category=""
                logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()
        except:
            textfirstpara=""
        if textfirstpara=="":
            try:
                textfirstpara=tree.xpath('//*[@id="content"]/article/section/div/div/p/text()')[0]
            except:
                textfirstpara=" "
                logger.info("oops - geen first para")
        try:
            textrest=tree.xpath('//*[@id="content"]/article/section/div/div/p/text() | //*[@id="content"]/article/section/div/div/p/i/text() | //*[@id="content"]/article/section/div/div/p/a/text() | //*[@id="content"]/article/section/div/div/h2/text() | //*[@id="content"]/article/section/div/h2/text() | //*[@id="content"]/article/section/div/div/table/tbody/tr/td/text()')
        except:
            logger.info("oops - geen text?")
            textrest=""
        text ="\n".join(textrest)
        try:
            author_door=tree.xpath('//*[@id="content"]/article/section/div/div/div/span/text()')[0]
        except:
            author_door=""
            logger.info("No 'author' field encountered - don't worry, maybe it just doesn't exist.")
        author_bron=""
        text=polish(text)

        images = nos._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img = element.xpath('//figure[@class="article_head_image block_largecenter"]//img') [0]
            image = {'url' : img.attrib['src'],
                 #'height' : img.attrib['height'],
                 #'width' : img.attrib['width'],
                 #'caption' : element.xpath(element.xpath('.//div[@Class="caption_content"]/text()')),
                 'alt' : img.attrib['alt']}
            if image['url'] not in [i['url'] for i in images]:
                images.append(image)
        return images


class volkskrant(rss):
    """Scrapes volkskrant.nl """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "volkskrant (www)"
        self.rss_url='http://www.volkskrant.nl/nieuws/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)


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
                logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()
        except:
            textfirstpara=""
        if textfirstpara=="":
            try:
                textfirstpara=tree.xpath('//*/header/p/text()')[1].replace("\n", "").strip()
            except:
                textfirstpara=" "
                logger.info("oops - geen first para")
        try:
            #1. path: regular textrest
            #2. path: textrest version found in 2014 11 16
            #3. path: second heading found in 2014 11 50
            #4. path: text with link behind; found in 2014 10 2455(html-file-nr)
            #5. path: old design regular text
            #6. path: old design second heading
            #7. path:old design text with link
            textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() | //*[@class="article__body__container"]/p[*]/text() | //*[@class="article__body__container"]/h3/text() | //*[@class="article__body__container"]/p/a/text() | //*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/p/strong/text() | /*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/p/a/text() | //*/p[@class="article__body__paragraph first"]/text() | //*/div[@class="article__body"]/h2/text() | //*/p[@class="article__body__paragraph first"]/a/text() | //*/p[@class="article__body__paragraph"]/text() | //*/h3[@class="article__body__container-title"]/text()')
        except:
            logger.info("oops - geen text?")
            textrest=""
        text = textfirstpara + "\n"+ "\n".join(textrest)
        try:
            author_door=" ".join(tree.xpath('//*/span[@class="author"]/*/text() | //*/span[@class="article__body__container"]/p/sub/strong/text() |//*/span[@class="article__author"]/span/text()' )).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
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
        if author_door=="":
            try:
                author_door=" ".join(tree.xpath('//*[@class="article__meta--v2"]/span/span[2]/text()')).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:")
            except:
                logger.info("No 'author' field encountered - don't worry, maybe it just doesn't exist.")
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
                    logger.info("No 'press-agency source ('bron')' field encountered - don't worry, maybe it just doesn't exist.")
        if author_door=="" and author_bron=="" and category=="Opinie":
            author_door = "OPINION PIECE OTHER AUTHOR"
        text=polish(text)

        images = volkskrant._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images}

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
        link="http://www.volkskrant.nl//cookiewall/accept?url="+link
        return link 
 


class nrc(rss):
    """Scrapes nrc.nl """
    def __init__(self,database=True):
        self.database = database
        self.doctype = "nrc (www)"
        self.rss_url='http://www.nrc.nl/rss.php?n=np'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=9, day=10)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section     sth. like economy, sports, ..
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        tree=fromstring(htmlsource)

        try:
            category = tree.xpath('//*[@id="broodtekst"]/a[1]/text()')[0]
        except:
            category = ""
        if category=="":
            try:
                category=tree.xpath('//*[@class="article__section-branding"]/text()')[0]
            except:
                category=""
        try:
        #1. path: type 1 layout: regular text                                          
        #2. path: type 1 layout: text with link behind                                 
        #3. path: type 1 layout: text bold                                             
        #4. path: type 1 layout: text bold and italic                                  
        #5. path: type 2 layout: normal text first paragraph                            
        #6. path: type 2 layout: text with link behind                                  
        #7. path: type 1 layout: italic text, found in 2014 11 988                  
        #8. path for in beeld found 2015 11 13          
            textfirstpara=tree.xpath('//*[@class="eerste"]/text() | //*[@class="eerste"]/a/text() | //*[@class="eerste"]/strong/text() | //*[@class="eerste"]/strong/em/text() | //*[@id="article-content"]/p[1]/text() | //*[@id="article-content"]/p[1]/a/text() | //*[@class="eerste"]/em/text() | //*[@class="intro"]/text() | //*[@class="intro"]/p/text() | /*[@class="intro"]/p/span/text()')
            textfirstpara = " ".join(textfirstpara)
        except:
            textfirstpara=""
            logger.info("Ooops geen first para")
        try:
        #1. path: type 1 layout: regular text                                         
        #2. path: type 1 layout: second heading in regular text                         
        #3. path: type 2 layout: text in different layout, found in 2014 12 11         
        #4. path: type 2 layout: bold text, found in 2014 12 11                        
        #5. path: type 2 layout: text with underlying link, found in 2014 12 11        
        #6. path: type 2 layout: italic text, found in 2014 12 11                      
        #7. path: type 2 layout: second heading found in 2014 12 11                    
        #8. path: type 2 layout: text in grey box/ speech bubble                       
        #9. path: type 1 layout: text with link behind                                 
        #10.path: type 1 layout: text in grey box/ speech bubble                      
        #11. path: type 1 layout: bold text found in 2014 12 198                      
        #12. path: type 1 layout: italix text with link behind, found in 2014 12 198 !!!!!not working :(                                                                       
        #13. path: type 3 layout: regular text found in 2014 11 62                     
        #14. path: type 3 layout: text with link behind found in 2014 11 63            
        #15. path: type 3 layout: italic text with link behind, found in 2014 11 63    
        #16. path: type 1 layout: italix text, found in 2014 04 500                   
        #17. path: type 1 layout: found 2015 11 13                                    
        #17. path: type 1 layout: heading in regular text found 2015 11 13            
        #18. live feed subheading "old news"                                          
        #19. live feed text "old news"                                                 
        #20. live feed textlink "oldnews"                                              
        #21. live feed list "old news"                                                
        #21. live feed subheading "new news"                                          
        #22. live feed text "new news"                                                
        #23. live feed textlink "new news"                                             
        #24. live feed names "new news"                                            
        #24. path type 1 layout: subheading in regular text found 2015 11 16       
        #25. path type 1 layout: text in link found on 2015 11 16 
        #26. path regular layout: bold subtitle found 2015 11 16
            textrest=tree.xpath('//*[@id="broodtekst"]/p[position()>1]/text() | //*[@id="broodtekst"]/h2/text() | //*[@id="article-content"]/p[position()>1]/text() | //*[@id="article-content"]/p[position()>1]/strong/text() | //*[@id="article-content"]/p[position()>1]/a/text() | //*[@id="article-content"]/p[position()>1]/em/text() | //*[@id="article-content"]/h2/text() | //*[@id="article-content"]/blockquote/p/text() | //*[@id="broodtekst"]/p[position()>1]/a/text() | //*[@id="broodtekst"]/blockquote/p/text() | //*[@id="broodtekst"]/p[position()>1]/strong/text() | //*[@id="broodtekst"]/p[position()>1]/a/em/text() | //*[@class="beschrijving"]/text() | //*[@class="beschrijving"]/a/text() | //*[@class="beschrijving"]/a/em/text() | //*[@id="broodtekst"]/p[position()>1]/em/text() | //*[@class="content article__content"]/p[position()>0]/text() | //*[@class="content article__content"]/p/strong/text() | //*[@class="content article__content"]/p/a/text() | //*[@class="content article__content"]/blockquote/p/text() | //*[@class="bericht"]/h2/text() | //*[@class="bericht"]/p/text() | //*[@class="bericht"]/p/a/text() |//*[@class="bericht"]/ul/li/text() | //*[@class="bericht bericht--new"]/h2/text() | //*[@class="bericht bericht--new"]/p/text() | //*[@class="bericht bericht--new"]/p/a/text() | //*[@class="bericht bericht--new"]/p/em/text() | //*[@class="content article__content"]/h2/text() | //*[@class="content article__content"]/h3/text() | //*[@class="content article__content"]/p/a/em/text() | //*[@class="content article__content"]/blockquote/p/strong/text() | //*[@class="content article__content"]/p/br/a/strong/text() | //*[@class="content article__content"]/p/em/text()')
        except:
            logger.info("oops - geen text?")
            textrest = ""
        text = textfirstpara + "\n"+ "\n".join(textrest)
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
        author_bron=""
        if textnew=="" and category=="" and author_door=="":
            logger.info("No article-page?")
            try:
                if tree.xpath('//*[@class="kies show clearfix"]/h2/text()')[0] == 'Lees dit hele artikel':
                    text="THIS SEEMS TO BE AN ARTICLE ONLY FOR SUBSCRIBERS"
                    logger.warning(" This seems to be a subscribers-only article")
            except:
                    text=""
        text=polish(text)
        
        images = nrc._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="responsive-img-div img-b1bc3f75894aebe980b93536058622c9  loaded"]//img')
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
    def __init__(self,database=True):
        self.database = database
        self.doctype = "parool (www)"
        self.rss_url='http://www.parool.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
            category=re.findall("/+[a-z]+/", link)[0]
            category=category.replace("/","")
        except:
            category=""
        if category=="":
            try:
                category=re.findall("/+[a-z]+-+[a-z]+-+[a-z]+/", link)[0]
                category = category.replace("/","")
            except:
                category=""
                logger.info("geen category")
        try:
            textfirstpara=tree.xpath('//*[@id="page-main-content"]//*[@class="article__intro"]/text() | //*[@id="art_box2"]//*[@class="intro2"]/a/text()')
            textfirstparanew=" ".join(textfirstpara)
        except:
            textfirstpara=" "
            logger.info("oops - geen textfirstpara")
        try:
        #1. Regular text (version 07/03/16)                                            
        #2. Bold text - subtitles                                                      
        #3. Link text                                                                  
        #4. Embedded text subtitle one                                                 
        #5. Embedded text subitles rest                                                
            textrest=tree.xpath('//*[@id="page-main-content"]//*[@class="article__body__container"]/p/text() | //*[@id="page-main-content"]//*[@class="article__body__container"]/p/a/text() | //*[@id="page-main-content"]//*[@class="article__body__container"]/p/strong/text() | //*[@id="page-main-content"]//*[@class="media-container"]/div/h3/text() | //*[@id="page-main-content"]//*[@class="media-container"]/div/div/p/text() | //*[@class="article__body__paragraph first"]/text() | //*[@class="article__body__paragraph first"]/strong/text() | //*[@class="article__body__paragraph first"]/a/text() | //*[@class="article__body__paragraph"]/text() | //*[@class="article__body__paragraph"]/strong/text()')
        except:
            textrest=" "
            logger.info("oops - geen textrest")
        text=textfirstparanew + "\n" + "\n".join(textrest)
        author_text=tree.xpath('//*[@id="page-main-content"]//*[@class="article__footer"]/span/span/span/text()')
        try:
            author_door=[e for e in author_text if e.find("Door")>=0][0].strip().replace("(","").replace(")","").replace("Door:","")
        except:
            author_door=""
        if author_door=="":
            try:
                author_door=[e for e in author_text if e.find("Bewerkt door:")>=0][0].strip().replace("(","").replace(")","").replace("Bewerkt door:","")
            except:
                author_door=""
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
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
                logger.info("No 'press-agency source ('bron')' field encountered - don't worry, maybe it just doesn't exist.")
        text=polish(text)

        images = parool._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images": images}

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
    def __init__(self,database=True):
        self.database = database
        self.doctype = "trouw (www)"
        self.rss_url='http://www.trouw.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)


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
            category=tree.xpath('//*[@id="subnav_nieuws"]/li/a/span/text()')[0]
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
                logger.info("oops - geen category")
        try:
        #1. Regular text - intro                                                       
        #2. Bold text - subtitles                                                      
        #3. Regular  text                                                              
        #4. Extra box title                                                            
        #5. Extra box text                                                             
        #6. Link text                                                                  
        #7. Explanantion box text                                                      
        #8. italics                                                                    
            textrest=tree.xpath('//*[@class="article__section-title__text heading-3"]/text() | //*[@class="article__paragraph"]/text() | //*[@class="article__quote__text"]/text() | //*[@class="article__framed-text__title"]/text() | //*[@id="art_box2"]/section/p/text() |  //*[@id="art_box2"]/p/a/text() |  //*[@id="art_box2"]//*[@class="embedded-context embedded-context--inzet"]/text() |  //*[@id="art_box2"]/p/em/text()')
        except:
            textrest=" "
            logger.info("oops - geen textrest")
        text = "\n".join(textrest)
        try:
             author_door=tree.xpath('//*[@class="author"]/text()')[0]               
        except:
             author_door=" "
             logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
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
                    logger.info("No 'press-agency source ('bron')' field encountered - don't worry, maybe it just doesn't exist.")

        text=polish(text)

        images = trouw._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

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
    def __init__(self,database=True):
        self.database = database
        self.doctype = "telegraaf (www)"
        self.rss_url='http://www.telegraaf.nl/rss/'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
            category = tree.xpath('//*[@class="selekt"]/text() | //*[@class="topbar"]/div/a[2]/text()' )[0]
        except:
            category = ""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
        try:
        #1.path: layout 1: regular first para                                          
        #2.path: layout 2 (video): regular first (and mostly only) para               
        #3.path: layout 1: second version of first para, fi 2014 11 6                  
        #4.path layout 1: place found on 2015 11 16                                    
        #5.path: regular first para found 2016 04 07                                   
            textfirstpara=tree.xpath('//*[@class="zak_normal"]/p/text() | //*[@class="bodyText streamone"]/div/p/text() | //*[@class="zak_normal"]/text() | //*[@class="zak_normal"]/span/text() | //*[@id="main"]/div/div/p/text()')
            textfirstpara = " ".join(textfirstpara)
        except:
            textfirstpara=""
            logger.info("OOps - geen textfirstpara?")
        try:
        #1. path: layout 1: regular text, fi 2014 12 006                               
        #2. path: layout 1: text with link, fi 2014 12 006                             
        #3. path: layout 1: second heading, fi 2014 12 015                             
        #4. path: layout 1: bold text, fi 2014 12 25                                   
        #5. path: layout 1: italic text, fi 2014 09 5200                               
        #6. path: layout 1: second headings, fi 2014 07 84                             
        #7. path: layout 2: reagular text, found 2016 04 07                             
        #8. path: layout 2: italic text, found 2016 04 07                               
        #9. path: layout 2: bold text, found 2016 04 07                                
            textrest=tree.xpath('//*[@id="artikelKolom"]/p[not (@class="tiptelegraaflabel")]/text() | //*[@id="artikelKolom"]/p/a/text() | //*[@id="artikelKolom"]/h2/strong/text() | //*[@id="artikelKolom"]/p/strong/text() | //*[@id="artikelKolom"]/p/em/text() | //*[@id="artikelKolom"]/h2[not (@class="destination trlist")]/text() | //*[@class="broodtekst"]/p/text() | //*[@class="broodtext"]/h2/strong/text() | //*[@id="artikelKolom"]/div/p/text() | //*[@id="artikelKolom"]/div/p/em/text() | //*[@id="artikelKolom"]/div/p/strong/text() | //*[@id="artikelKolom"]/div/h2/text() | //*[@id="artikelKolom"]/div/p/a/text() | //*[@class="ui-abril ui-text-small"]/p/text()')
        except:
            logger.info("oops - geen texttest?")
            textrest = ""
        text = textfirstpara + "\n"+ "\n".join(textrest)
        try:
            author_door = tree.xpath('//*[@class="auteur"]/text() | //*[@class="ui-table ui-gray3"]/span[2]/text()')[0].strip().lstrip("Van ").lstrip("onze").lstrip("door").strip()
        except:
            author_door = ""
        author_bron=""
        text=polish(text)

        images = telegraaf._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip(),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@class="image ui-bottom-margin-3 ui-top-margin-2 img-left"]//img')
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

class metronieuws(rss):
    """Scrapes metrnieuwso.nl """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "metro (www)"
        self.rss_url='http://www.metronieuws.nl/rss.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)

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
            category = tree.xpath('//*[@class="active"]/text()')[0]
        except:
            category = ""
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
            logger.info("oops - geen textrest?")
            textrest = ""
        text = "\n".join(textrest)
        text=re.sub("Lees ook:"," ",text)
        try:
        #new layout author:                                                            
            author_door = tree.xpath('//*[@class="username"]/text()')[0].strip().lstrip("door ").lstrip("© ").lstrip("2014 ").strip()
        except:
            author_door = ""
        if author_door=="":
        #try old layout author                                                         
            try:
                author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
            except:
                author_door = ""
        author_bron=""
        text=polish(text)

        images = metronieuws._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
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

    def __init__(self,database=True):
        self.database = database
        self.doctype = "geenstijl"
        self.rss_url='http://www.geenstijl.nl/index.xml'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=9, day=15)

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
        textrest=tree.xpath('//*[@id="content"]/article/text() | //*[@id="content"]/article/a/text() | //*[@id="content"]/article/em/text() | //*[@id="content"]/article/strong/text() | //*[@id="content"]/article/s/text() |  //*[@id="content"]/article/p/text() | //*[@id="content"]/article/p/a/text() | //*[@id="content"]/article/p/s/text() | //*[@id="content"]/article/p/em/text() | //*[@id="content"]/article/p/strong/text() | //*[@id="content"]/article/p/strong/a/text() | //*[@id="content"]/article/p/em/a/text() | //*[@id="content"]/article/blockquote/p/text() | //*[@id="content"]/article/blockquote/text() | //*[@id="content"]/article/blockquote/a/text()')
        if textrest=="":
            logger.info("OOps - empty textrest for?")
        text="\n".join(textrest)
        try:
            author_door=tree.xpath('//*[@id="content"]/article/footer/text()')[0].replace("|","")
        except:
            author_door=""

        text=polish(text)

        images = geenstijl._extract_images(self,tree)

        extractedinfo={"text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "images":images}

        return extractedinfo

    def _extract_images(self, dom_nodes):
        images = []
        for element in dom_nodes:
            img_list = element.xpath('//*[@id="content"]//img')
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

class fok(rss):
    """Scrapes volkskrant.nl """

    def __init__(self,database=True):
        self.database = database
        self.doctype = "fok"
        self.rss_url='http://rss.fok.nl/feeds/nieuws'
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=2)


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
            category="".join(tree.xpath('//*[@id="crumbs"]/ul/li/a/text()'))
        except:
            category = ""
        if len(category.split(" ")) >1:
            category=""
        try:
            textrest=tree.xpath('//*[@role="main"]/article/p/text() | //*[@role="main"]/article/p/strong/text() | //*[@role="main"]/article/p/strong/a/text() | //*[@role="main"]/article/p/a/text() | //*[@role="main"]/article/p/em/text() | //*[@id="mainContent"]//*[@role="main"]/article/p/text() | //*[@id="mainContent"]/div[5]/main/article/p/text()')
        except:
            print("geen text")
            logger.info("oops - geen textrest?")
            textrest = ""
        text = "\n".join(textrest)
        textnew=re.sub("Lees ook:"," ",text)
        try:
             author_door = tree.xpath('//*[@class="mainFont"]/text()')[0].strip()
        except:
            author_door = ""
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
                logger.info("No 'press-agency source ('bron')' field encountered - don't worry, maybe it just doesn't exist.")
        textnew=polish(textnew)

        images = fok._extract_images(self,tree)

        extractedinfo={"category":category.strip(),
                       "text":textnew.strip(),
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

    def __init__(self,database=True):
        self.database=database
        self.doctype = "destentor (www)"
        self.rss_url="http://www.destentor.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=3)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
    #        teaser = tree.xpath('//*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/span/text() |  //*/p[@class="article__intro"]/span/b/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
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

    def __init__(self,database=True):
        self.database=database
        self.doctype = "bd (www)"
        self.rss_url="http://www.bd.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=9)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
        except:
            teaser=""
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
  

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.bd.nl///cookiewall/accept?url="+link
        return link

class gelderlander(rss):
    """Scrapes gelderlander.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "gelderlander (www)"
        self.rss_url="http://www.gelderlander.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=10)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.info("OOps - geen eerste alinea?")
        #1. path: regular text                                                                                                     
        #2. path: text with link behind (shown in blue underlined);                                        
        #3. path: second headings 
        text=" ".join(tree.xpath('//*/p[@class="article__paragraph"]//text() | //*/p[@class="liveblog_time-text"]//text() | //*/time[@class="liveblog__time-text"]//text() | //*/p[@class="liveblog__intro"]//text() | //*/p[@class="liveblog__paragraph"]//text()')).strip()
        #text = tree.xpath('//*/p[@class="article__paragraph"]/span/text() | //*/p[@class="article__paragraph"]/a/text() | //*/p[@class="article__paragraph"]/h2/text() | //*/h2[@class="article__subheader"]/text() | //*/p[@class="article__paragraph"]/b/text() | //*/p[@class="article__paragraph"]/text() | //*/p[@class="article__paragraph"]/i/text() | //*/p[@class="article__paragraph"]/a/i/text()')
        if text=="":
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
  

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.gelderlander.nl///cookiewall/accept?url="+link
        return link

class ed(rss):
    """Scrapes ed.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "ed (www)"
        self.rss_url="http://www.ed.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=10)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
        try:
            teaser=" ".join(tree.xpath('//*/p[@class="article__intro"]//text() | //*/p[@class="article__intro video"]//text()')).strip()
#            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
  

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.ed.nl///cookiewall/accept?url="+link
        return link

class bndestem(rss):
    """Scrapes bndestem.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "bndestem (www)"
        self.rss_url="http://www.bndestem.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
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
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
  

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.bndestem.nl///cookiewall/accept?url="+link
        return link

class pzc(rss):
    """Scrapes pzc.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "pzc (www)"
        self.rss_url="http://www.pzc.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
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
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
  

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.pzc.nl///cookiewall/accept?url="+link
        return link

class tubantia(rss):
    """Scrapes tubantia.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "tubantia (www)"
        self.rss_url="http://www.tubantia.nl/home/rss.xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@class="article__title"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
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
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
  

    def getlink(self,link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.tubantia.nl///cookiewall/accept?url="+link
        return link

class limburger(rss):
    """Scrapes limburger.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "limburger (www)"
        self.rss_url="http://feeds.feedburner.com/Limburgernl-nieuws?format=xml"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=17)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*/h1[@itemprop="name"]/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
        # 2. path = video articles
        # 3. path = articles that are tagged 'Home'
            category = tree.xpath('//*[@class="container"]/ul/li[@class="sub-nav__list-item active"]/a/text() | //*[@class="article__section-text"]/a/text() | //*/span[@class="mobile-nav__list-text"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
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
            logger.info("OOps - geen eerste alinea?")
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
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text.strip(),
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo

class frieschdagblad(rss):
    """Scrapes frieschdagblad.nl"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "frieschdagblad (www)"
        self.rss_url="http://www.frieschdagblad.nl/nieuws.asp"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=10)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*[@class="ArtKopStd"]/b/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
            category = tree.xpath('//*/span[@class="rubriek"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
        #no teaser
        try:
            teaser=tree.xpath('//*/p[@class="article__intro"]/span[@class="tag"]/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text() | //*/p[@class="article__intro"]/b/text() | //*/p[@class="article__intro video"]/text() | //*/p[@class="article__intro video"]/span/text() | //*/p[@class="article__intro video"]/span/a/text()')[0]
        except:
            teaser=""
            logger.info("OOps - geen eerste alinea?")
        #1. path: regular text                                                                                                     
        text = tree.xpath('//*[@class="ArtTekstStd"]/text()')
        if text=="":
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

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

    def __init__(self,database=True):
        self.database=database
        self.doctype = "zwartewaterkrant (www)"
        self.rss_url="http://www.zwartewaterkrant.nl/rss.php"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=5, day=10)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''
        try:
            tree = fromstring(htmlsource)
        except:
            print("kon dit niet parsen",type(doc),len(doc))
            print(doc)
            return("","","", "")
        try:
            title = tree.xpath('//*[@id="containerContent"]/h2/text()')[0]
        except:
            title=""
            logger.info("OOps - geen titel?")
        try:
        # 1. path = normal articles
            category = tree.xpath('//*/span[@class="rubriek"]/text()')[0]
        except:
            category=""
            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")                                                                       
        try:
            teaser=tree.xpath('//*/span[@class="blackbold"]/text()')[0]
        except:
            teaser=""
            logger.info("OOps - geen eerste alinea?")
        #1. path: regular text                                                                                                     
        text = tree.xpath('//*[@id="containerContent"]/p/text() | //*[@id="containerContent"]/p/a/text()')
        if text=="":
            logger.info("OOps - empty text")
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
                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
        except:
            author_bron=""

        # text=polish(text)

        extractedinfo={"title":title.strip(),
                       "category":category.strip(),
                       "teaser":teaser.strip(),
                       "text":text,
                       "byline":author_door.replace("\n", " "),
                       "byline_source":author_bron.replace("\n"," ").strip()
                       }

        return extractedinfo
