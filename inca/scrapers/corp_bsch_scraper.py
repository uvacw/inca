import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class bsch(Scraper):
    """Scrapes Banco Santander Central Hispano"""

    def __init__(self):
        self.START_URL = "http://www.santander.com/csgs/Satellite?appID=santander.wc.CFWCSancomQP01&c=GSInformacion&canal=CSCORP&cid=1278687978582&empr=CFWCSancomQP01&leng=en_GB&pagename=CFWCSancomQP01%2FGSInformacion%2FCFQP01_GSInformacionDetalleSimple_PT08"
        self.BASE_URL = "http://www.santander.com"
        self.doctype = "BSCH (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=1)
        self.releases = []

    def process_links(self, links):
        for link in links:
            logger.debug("ik ga nu {} ophalen".format(link))
            try:
                tree = fromstring(requests.get(link).text)
                try:
                    title = " ".join(tree.xpath('//*/h3[@class="titulo01"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    d = tree.xpath('//*[@class="bloque_Wfecha02"]//text()')[0].strip()
                    print(d)
                    jaar = int(d[-4:])
                    maand = int[d[3:-5]]
                    dag = int(d[:2])
                    print(jaar)
                    print(maand)
                    print(dag)
                    datum = datetime.datetime(jaar, maand, dag)
                except Exception as e:
                    print("could not parse date")
                    print(e)
                    datum = None
                try:
                    teaser = " ".join(
                        tree.xpath('//*[@class="bloque_Wtexto webedit"]/ul//text()')
                    )
                except:
                    print("no teaser")
                    teaser = ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text = " ".join(
                        tree.xpath('//*[@class="bloque_Wtexto webedit"]/p//text()')
                    )
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                self.releases.append(
                    {
                        "text": text.strip(),
                        "date": datum,
                        "title": title.strip(),
                        "teaser": teaser.strip(),
                        "url": link.strip(),
                    }
                )
            except:
                print("no connection:\n" + link)

    def get(self, save):
        """                                                                             
        Fetches articles from Banco Santander Central Hispano
        """

        """ Process the actual/latest page first """
        current_url = self.START_URL
        tree = fromstring(
            requests.get(current_url)
            .text.replace("csstg", "csgs")
            .replace("http://staging.aacc.gs.corp", self.BASE_URL)
        )

        linkobjects = tree.xpath('//*[@class="bloque_text01 webedit"]/p//a')
        links = [l.attrib["href"] for l in linkobjects if "href" in l.attrib]
        # print('\n'.join(links))
        self.process_links(links)

        """ Now grab the yearlinks from the actual/latest page """
        tree = fromstring(requests.get(self.START_URL).text)
        yearobjects = tree.xpath('//*[@class="bloque_text01 webedit"]/ul/li//a')
        year_links = [
            self.BASE_URL + l.attrib["href"] for l in yearobjects if "href" in l.attrib
        ]

        for year_link in year_links:
            tree = fromstring(
                requests.get(year_link)
                .text.replace("csstg", "csgs")
                .replace("http://staging.aacc.gs.corp", self.BASE_URL)
            )

            linkobjects = tree.xpath('//*[@class="bloque_text01 webedit"]/p/strong//a')
            links = [
                self.BASE_URL + l.attrib["href"]
                for l in linkobjects
                if "href" in l.attrib
            ]
            self.process_links(links)

        return self.releases
