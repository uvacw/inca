# Scraper starts at 1999, as from this year there are PDFs

import requests
import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")


class romanianparliament(Scraper):
    """Scrapes Romanian parliament"""

    def __init__(self):
        self.BASE_URL = "http://www.cdep.ro/pls/parlam/"
        self.doctype = "romanianparliament (par)"
        self.version = ".1"
        self.date = datetime.datetime(year=2018, month=6, day=13)

    def get(self, save):
        """                                                                             
        Fetches questions from Romanian parliament
        """

        releases = []

        year = 1999

        while True:
            try:

                page = requests.get(
                    self.BASE_URL + "interpelari.lista?tip=&dat=" + str(year) + "&idl=2"
                )

                if page.text.find("Question no.") == -1:
                    logger.info(str(year) + " niet gevonden")
                    break

                tree = fromstring(page.text)
                linkobjects = tree.xpath('//*[@id="pageContent"]//tr/td/b/a')
                links = [self.BASE_URL + l.attrib["href"] for l in linkobjects]

                for link in links:
                    logger.debug("ik ga nu {} ophalen".format(link))
                    current_page = requests.get(link)
                    tree = fromstring(current_page.text)
                    try:
                        title = "".join(
                            tree.xpath('//*[@id="pageContent"]/p[1]/span//text()')
                        ).strip()
                    except:
                        logger.info("no title")
                        title = ""
                    try:
                        d = tree.xpath(
                            '//*[@id="pageContent"]/dd/table/tr[3]/td[2]/b//text()'
                        )[0].strip()
                        jaar = int(d[-4:])
                        maand = int(d[-7:-5])
                        dag = int(d[-10:-8])
                        datum = datetime.datetime(jaar, maand, dag)
                    except Exception as e:
                        logger.info("could not parse date")
                        logger.info(e)
                        datum = None
                    try:
                        questioners = "".join(
                            tree.xpath(
                                '//*[@id="pageContent"]/dd/table/tr[*]/td[2]/b/a//text()'
                            )
                        ).strip()
                    except Exception as e:
                        logger.info(e)
                        questioners = ""
                        questioners_clean = " ".join(members.split())
                    try:
                        questioners_party = "".join(
                            tree.xpath(
                                '//*[@id="pageContent"]/dd/table/tr[*]/td[2]/a//text()'
                            )
                        ).strip()
                    except:
                        questioners_party = ""
                        questioners_party_clean = " ".join(questioners_party.split())
                    try:
                        text = ""
                    except:
                        logger.info("oops - geen textrest?")
                    try:
                        pdf_url = "".join(
                            tree.xpath(
                                '//*[@id="pageContent"]/dd/table/tr[9]/td[2]/table/tr/td[3]/b/a/@href'
                            )
                        ).strip()
                        self.create_pdf(pdf_url)
                    except:
                        pdf_url = ""
                        pdf_url_clean = " ".join(pdf_url.split())
                    releases.append(
                        {
                            "title": title.strip(),
                            "text": text.strip(),
                            "questioners": questioners.strip(),
                            "questioners_party": questioners_party,
                            "date": datum,
                            "pdf_url": pdf_url,
                            "url": link.strip(),
                        }
                    )
                year += 1

            except Exception as e:

                logger.info(e)
                break

        return releases

    # def create_pdf(self, url):
    #    try:
    #        print(self.BASE_URL + url[1:])
    #        r = requests.get(self.BASE_URL + url[1:], allow_redirects=True)


#
#        with open('/Users/tamara/Downloads/'+ url.split('/')[-1], 'wb') as f:
#            f.write(r.content)
#    except Exception as e:
#        print(e)
