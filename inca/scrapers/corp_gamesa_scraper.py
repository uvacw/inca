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

MAAND2INT = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


class gamesa(Scraper):
    """Scrapes Gamesa"""

    def __init__(self):
        self.START_URL = "http://www.gamesacorp.com/"
        self.BASE_URL = "http://www.gamesacorp.com/"
        self.doctype = "Gamesa (corp)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=8, day=21)

    def get(self, save):
        """                                                                             
        Fetches articles from Gamesa
        """

        releases = []

        page = 1
        current_url = (
            self.START_URL
            + "en/tratarAplicacionNoticia.do?idCategoria=0&fechaDesde=&especifica=0&texto=&idSeccion=0&paginaActual="
            + str(page)
            + "&fechaHasta="
        )
        overview_page = requests.get(current_url)
        while (
            overview_page.content.find(
                b"The page you have requested cannot be displayed."
            )
            == -1
        ):

            tree = fromstring(overview_page.text)

            linkobjects = tree.xpath('//*/li[@class="impar itemlistado"]/span//a')
            links = [l.attrib["href"] for l in linkobjects if "href" in l.attrib]

            for link in links:
                logger.debug("ik ga nu {} ophalen".format(link))
                current_page = requests.get(link)
                tree = fromstring(current_page.text)
                try:
                    title = " ".join(tree.xpath('//*/h3[@class="nombre"]/text()'))
                except:
                    print("no title")
                    title = ""
                try:
                    d = tree.xpath('//*/p[@class="fecha"]//text()')[0].strip()
                    print(d)
                    jaar = int(d[-4:])
                    maand = MAAND2INT[d[2:-4].strip()]
                    dag = int(d[:2])
                    datum = datetime.datetime(jaar, maand, dag)
                except Exception as e:
                    print("could not parse date")
                    print(e)
                    datum = None
                try:
                    teaser = "".join(
                        tree.xpath('//*[@class="descripcion"]/ul//text()')
                    ).strip()
                except:
                    teaser = ""
                    teaser_clean = " ".join(teaser.split())
                try:
                    text = " ".join(tree.xpath('//*[@class="modulo2"]/p//text()'))
                except:
                    logger.info("oops - geen textrest?")
                    text = ""
                text = "".join(text)
                releases.append(
                    {
                        "text": text.strip(),
                        "date": datum,
                        "title": title.strip(),
                        "teaser": teaser.strip(),
                        "url": link.strip(),
                    }
                )

            page += 1
            current_url = (
                self.START_URL
                + "en/tratarAplicacionNoticia.do?idCategoria=0&fechaDesde=&especifica=0&texto=&idSeccion=0&paginaActual="
                + str(page)
                + "&fechaHasta="
            )
            overview_page = requests.get(current_url)

        return releases
