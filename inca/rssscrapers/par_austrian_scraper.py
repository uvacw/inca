import requests
import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
import feedparser
import re
import logging
import urllib

logger = logging.getLogger("INCA")


class austrianparliament(rss):
    """Scrapes Austrian Parliament"""

    def __init__(self):
        self.doctype = "austrianparliament (par)"
        self.rss_url = "https://www.parlament.gv.at/PAKT/JMAB/filter.psp?view=RSS&RSS=RSS&jsMode=RSS&xdocumentUri=%2FPAKT%2FJMAB%2Findex.shtml&view=RSS&NRBR=NR&GP=XXVI&ZEIT=J&JMAB=J_JPR_M&VHG2=ALLE&SUCH=&LISTE=Anzeigen&listeId=105&FBEZ=FP_005"
        self.version = ".1"
        self.BASE_URL = "https://www.parlament.gv.at/"
        self.date = datetime.datetime(year=2018, month=6, day=6)

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
        """

        tree = fromstring(htmlsource)
        try:
            t = "".join(tree.xpath('//*/h1[@id="inhalt"][1]//text()')).strip()
            title = re.sub("[\(].*?[\)]", "", t)
            logger.info(title)
        except:
            logger.warning("no title")
            title = ""
        try:
            d = tree.xpath(
                '//*[@id="content"]/div[3]/div[2]/table/tbody/tr[1]/td[1]//text()'
            )[0].strip()
            print(d)
            jaar = int(d[-4:])
            maand = int(d[-7:-5])
            dag = int(d[-10:-8])
            datum = datetime.datetime(jaar, maand, dag)
            logger.info(datum)
        except Exception as e:
            try:
                d = tree.xpath(
                    '//*[@id="content"]/div[3]/div[2]/div[2]/ul/li/a/text()'
                )[0].strip()
                # print(d)
                jaar = int(d[1:2])
                maand = int(d[4:5])
                dag = int(d[7:10])
                datum = datetime.datetime(jaar, maand, dag)
                # print(datum)
            except Exception as e:
                print("could not parse date")
                print(e)
                datum = None
        try:
            # try to get the questioners...
            q = "".join(
                tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/p[4]/a//text()')
            ).strip()
            # ... but if it does not contain 'eingebracht', then we grabbed the wrong thing and try sth alternative:
            if q.find("eingebracht") == -1:
                q = "".join(
                    tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/p[2]/a//text()')
                ).strip()
            questioners = re.sub("[\(].*?[\)]", "", q)
            print(questioners)
        except:
            try:
                q = "".join(
                    tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/p[3]/a//text()')
                ).strip()
            except Exception as e:
                questioners = ""
                questioners_clean = " ".join(members.split())
        try:
            questioners_party = re.findall(r"\((.*)\)", q)[0]
            print(questioners_party)
        except:
            questioners_party = ""
            questioners_party_clean = " ".join(questioners_party.split())
        try:
            text = " ".join(
                tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/p[1]//text()')
            ).strip()
            text = re.sub(r"\s+", " ", text)
            print(text)
        except Exception as e:
            try:
                text = " ".join(
                    tree.xpath('//*[@id="content"]/div[3]/div[2]/div[2]/p[2]//text()')
                ).strip()
                text = re.sub(r"\s+", " ", text)
                # print(text)
            except:
                logger.info("oops - no text?")
                text = ""
        release = {}
        # we first check whether there is a HTML version of the question
        try:
            html_url = "".join(
                tree.xpath(
                    '//*[@id="content"]/div[3]/div[2]/div[2]/div/ul/li[2]/a[2]/@href'
                )
            ).strip()
            r = requests.get(self.BASE_URL + html_url, allow_redirects=True)
            html_question = r.content
            tree2 = fromstring(html_question)
            text_question = "".join(
                tree2.xpath('//*[@class="WordSection1"]//text()')
            ).strip()
            release.update(
                {
                    "html_url": html_url,
                    "html_question": html_question,
                    "text_question": text_question,
                }
            )
        # if not, we grab the PDF-URL instead
        except Exception as e:
            print(e)
            try:
                pdf_url = "".join(
                    tree.xpath(
                        '//*[@id="content"]/div[3]/div[2]/div[2]/div/ul/li/a/@href'
                    )
                ).strip()
                r = requests.get(self.BASE_URL + pdf_url, allow_redirects=True)
                release.update({"pdf_url": pdf_url})
            except Exception as e:
                print(e)
                logger.warning("no question found, neither as HTMl nor as PDF")

        text = "".join(text)
        release.update(
            {
                "title": title.strip(),
                "text": text.strip(),
                "questioners": questioners.strip(),
                "questioners_party": questioners_party,
                "date": datum,
            }
        )
        # print(release)
        return release
