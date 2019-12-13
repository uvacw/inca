# Questions that are 'tilbagetaget' (withdrawn) are not included

import requests
import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging
import urllib

logger = logging.getLogger("INCA")


class danishparliament(Scraper):
    """Scrapes Danish Parliament"""

    def __init__(self, database=True):
        self.database = database
        self.START_URL = "http://www.ft.dk/da/dokumenter/dokumentlister/alle_spoergsmaal?startDate=20050101&endDate=20180701&pageNumber="
        self.BASE_URL = "http://www.ft.dk/"
        self.doctype = "danishparliament (par)"
        self.version = ".1"
        self.date = datetime.datetime(year=2018, month=5, day=9)

    def get(self, save):
        """                                                                             
        Fetches questions from Danish parliament
        """

        releases = []

        page = 1
        current_url = self.START_URL + str(page)
        overview_page = requests.get(current_url)
        while overview_page.text.find("data-url") != -1:

            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*[@data-title="Titel"]//a')
            links = [
                self.BASE_URL + l.attrib["href"]
                for l in linkobjects
                if "href" in l.attrib
            ]

            for link in links:
                logger.debug("ik ga nu {} ophalen".format(link))
                current_page = requests.get(link)
                if current_page.text.find("tilbagetaget") == -1:
                    tree = fromstring(current_page.text)

                    if "/lovforslag/" in link:
                        self.process_version1(tree, releases, link, "lovforslag")
                    elif "/spoergsmaal/" in link:
                        self.process_version2(tree, releases, link, "spoergsmaal")
                    elif "/aktstykke/" in link:
                        self.process_version2(tree, releases, link, "aktstykke")
                    elif "/almdel/" in link:
                        self.process_version1(tree, releases, link, "almdel")
                    else:
                        logger.info("Unknown version")

            page += 1
            current_url = self.START_URL + str(page)
            overview_page = requests.get(current_url)

        return releases

    def process_version1(self, tree, releases, link, category):
        logger.info("Version 1")
        logger.info(category)
        try:
            title = "".join(
                tree.xpath(
                    '//*[@id="ContentArea"]/div[5]/div[6]/div/div/div/div/table/tr/td[2]/p//text()'
                )
            ).strip()
            title = re.sub(r"Spm.[ ,.]*", "", title).title()
        except Exception as e:
            try:
                title = "".join(
                    tree.xpath(
                        '//*[@id="ContentArea"]/div[5]/div[8]/div/div/div/div/table/tr/td[2]/p//text()'
                    )
                ).strip()
                title = re.sub(r"Spm.[ ,.]*", "", title).title()
            except Exception as e:
                logger.info("no title")
                title = ""
        try:
            d = tree.xpath('//span[contains(.,"Dato:")]/text()')[0].strip()
            # d = tree.xpath('//*[@class="case-document"]/div[@class="tingdok-normal"][3]/span//text()')[0].strip()
            jaar = int(d[-4:])
            maand = int(d[-7:-5])
            dag = int(d[-10:-8])
            datum = datetime.datetime(jaar, maand, dag)
        except Exception as e:
            logger.info("could not parse date")
            logger.info(e)
            datum = None
            # try:
            #    d = tree.xpath('//*[@id="ContentArea"]/div[5]/div[6]/div/div/div/div/table/tr/td[1]/dl/dd//text()')[0].strip()
            #    jaar = int(d[-4:])
            #    maand = int(d[-7:-5])
            #    dag = int(d[-10:-8])
            #    datum = datetime.datetime(jaar,maand,dag)
            #    logger.info(datum)
            # except Exception as e:
            #    logger.info('could not parse date')
            #    logger.info(e)
            #    datum = None
        try:
            q = "".join(
                [
                    x.xpath("following-sibling::a//text()")
                    for x in tree.xpath('//*/div/div//*[contains(text(), "Af:")]')
                ][-1]
            ).strip()
            questioners = re.sub("[\(].*?[\)]", "", q)
        except Exception as e:
            questioners = ""
            questioners_clean = " ".join(questioners.split())
        try:
            qp = "".join(
                tree.xpath('//*[@id="ContentArea"]/div[5]/div[1]/div/div[4]/a//text()')
            ).strip()
            questioners_party = re.findall(r"\((.*)\)", qp)[0]
        except:
            questioners_party = ""
            questioners_party_clean = " ".join(questioners_party.split())
        try:
            text = " ".join(
                tree.xpath(
                    '//*[@class="case-document"]/div[@class="tingdok-normal"][1]/span//text()'
                )
            ).strip()
        except:
            logger.info("oops - geen textrest?")
            text = ""
        try:
            pdf_url = "".join(
                tree.xpath(
                    '//*[@id="ContentArea"]/div[5]/div[6]/div/div/div/div/table/tr/td[2]/table/tr/td[2]/a[1]/@href'
                )
            ).strip()
            self.create_pdf(pdf_url)
        except:
            pdf_url = ""
            pdf_url_clean = " ".join(pdf_url.split())
        text = "".join(text)
        releases.append(
            {
                "title": title.strip(),
                "category": category,
                "text": text.strip(),
                "questioners": questioners.strip(),
                "questioners_party": questioners_party,
                "date": datum,
                "pdf_url": pdf_url,
                "url": link.strip(),
            }
        )

    def process_version2(self, tree, releases, link, category):
        logger.info("Version 2")
        logger.info(category)
        try:
            title = "".join(
                tree.xpath(
                    '//*[@id="ContentArea"]/div[5]/div[1]/div/div[1]/span//text()'
                )
            ).strip()
            title = title[title.index("Om") :]
        except:
            try:
                title = "".join(
                    tree.xpath(
                        '//*[@id="ContentArea"]/div[5]/div[7]/div/div/div/div/table/tr/td[2]//p//text()'
                    )
                ).strip()
            except:
                logger.info("no title")
                title = ""
        try:
            d = tree.xpath(
                '//*[@id="ContentArea"]/div[5]/div[1]/div/div[4]/span[2]//text()'
            )[0].strip()
            jaar = int(d[-4:])
            maand = int(d[-7:-5])
            dag = int(d[-10:-8])
            datum = datetime.datetime(jaar, maand, dag)
        except Exception as e:
            try:
                d = tree.xpath(
                    '//*[@class="panel-group case-info-configurable-spot"]/div/div/div/div[5]/span[1]//text()'
                )[0].strip()
                jaar = int(d[-4:])
                maand = int(d[-7:-5])
                dag = int(d[-10:-8])
                datum = datetime.datetime(jaar, maand, dag)
            except:
                logger.info("could not parse date")
                logger.info(e)
                datum = None
        try:
            q = "".join(
                tree.xpath('//*[@id="ContentArea"]/div[5]/div[1]/div/div[2]/a//text()')
            ).strip()
            questioners = re.sub("[\(].*?[\)]", "", q)
        except:
            questioners = ""
            questioners_clean = " ".join(questioners.split())
        try:
            qp = "".join(
                tree.xpath('//*[@id="ContentArea"]/div[5]/div[1]/div/div[2]/a//text()')
            ).strip()
            questioners_party = re.findall(r"\((.*)\)", qp)[0]
        except:
            questioners_party = ""
            questioners_party_clean = " ".join(questioners_party.split())
        try:
            text = ""
            svar_found = False
            rows = tree.xpath('//*[@class="row"]')
            for row in rows:
                row_text = "".join(
                    row.xpath(
                        'div[@class="col-sm-12"]/div/div/div/table/tr/td/p//text()'
                    )
                ).strip()
                if row_text.startswith("Svar"):
                    svar_found = True
                elif svar_found:
                    text = row_text
                    break
        except:
            logger.info("oops - geen textrest?")
            text = ""
        text = "".join(text)
        try:
            pdf_url = "".join(
                tree.xpath(
                    '//*[@id="ContentArea"]/div[5]/div[7]/div/div/div/div/table/tr/td[2]/table/tr/td[2]/a[1]/@href'
                )
            ).strip()
            self.create_pdf(pdf_url)
        except:
            pdf_url = ""
            pdf_url_clean = " ".join(pdf_url.split())
        releases.append(
            {
                "title": title.strip(),
                "category": category,
                "text": text.strip(),
                "questioners": questioners.strip(),
                "questioners_party": questioners_party,
                "date": datum,
                "pdf_url": pdf_url,
                "url": link.strip(),
            }
        )

    # def create_pdf(self, url):
    #    try:
    #        print(self.BASE_URL + url[1:])
    #        r = requests.get(self.BASE_URL + url[1:], allow_redirects=True)


#
#        with open('/Users/tamara/Downloads/'+ url.split('/')[-1], 'wb') as f:
#            f.write(r.content)
#    except Exception as e:
#        print(e)
