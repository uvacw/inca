from lxml import html
from urllib import request
from lxml.html import fromstring
from inca.scrapers.rss_scraper import rss
from inca.core.scraper_class import Scraper
import re
import feedparser
import logging
import datetime
import locale
import requests
from lxml import etree

logger = logging.getLogger("INCA")


class neuesdeutschland(rss):
    """Scrapes http://www.handelsblatt.com/ """

    def __init__(self):
        self.doctype = "neues deutschland (www)"
        self.rss_url = "https://www.neues-deutschland.de/rss/aktuell.php"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=12, day=28)

    def get(self, **kwargs):

        # creating iteration over the rss feed.
        req = request.Request("https://www.neues-deutschland.de/rss/aktuell.php")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        categories = tree.xpath("//channel//item//category/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")

        for link, xpath_date, title, category, description in zip(
            article_urls, dates, titles, categories, descriptions
        ):
            link = link.strip()

            try:
                req = request.Request(link)
                read = (
                    request.urlopen(req)
                    .read()
                    .decode(encoding="utf-8", errors="ignore")
                )
                tree = fromstring(read)
            except:
                logger.warning("HTML tree cannot be parsed")

            # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
            parag = tree.xpath("//*[@class='Content']/p//text()")
            text = ""
            for r in parag:
                text += " " + r.strip().replace("\xa0", " ").replace("| ", "")

            # Retrieve source, which is usually the second word of articles containing it, nested inside an <em> element.
            try:
                if tree.xpath("boolean(//*[@class='Content']/p[last()]/i/text())"):
                    # Using this arbitrary 15 len character to differentiate the potential existence of a researcher description vs. an actual source. The mag doesn't provide class to differentiate.
                    if (
                        len(tree.xpath("//*[@class='Content']/p[last()]/i/text()")[0])
                        < 15
                    ):
                        source = (
                            tree.xpath("//*[@class='Content']/p[last()]/i/text()")[0]
                            .strip()
                            .replace("(", "")
                            .replace(")", "")
                        )
                    else:
                        source = ""
                else:
                    source = ""
            except:
                source = ""

            # Create iso format date
            try:
                # Wed, 28 Dec 2016 06:56:52 +0100
                date = datetime.datetime.strptime(
                    xpath_date[5:], "%d %b %Y %H:%M:%S %z"
                ).isoformat()
            except:
                date = ""

            tags = []
            if tree.xpath("boolean(//div[@class='Stopper-Locked'])"):
                tags.append("paid")

            doc = dict(
                pub_date=date,
                title=title,
                text=text.strip(),
                summary=description,
                source=source,
                category=category,
                url=link,
                tags=tags,
            )
            doc.update(kwargs)

            yield doc
