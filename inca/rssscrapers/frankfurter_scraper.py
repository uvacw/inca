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


class frankfurter(rss):
    """Scrapes http://www.faz.net/ """

    def __init__(self):
        self.doctype = "frankfurter (www)"
        self.rss_url = "http://www.faz.net/rss/aktuell/"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=11, day=21)

    def get(self, **kwargs):
        """
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        """

        # creating iteration over the rss feed.
        req = request.Request("http://www.faz.net/rss/aktuell/")
        read = request.urlopen(req).read()
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")

        for link, date in zip(article_urls, dates):  # you go to each article page
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
                logger.error("HTML tree cannot be parsed")

            # Check if the article is in wide format (storytelling or standard form)
            if tree.xpath("boolean(//*[@class='storytellingPage'])"):

                # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
                parag = tree.xpath("//*[@class='text']/p/text()")
                text = ""
                for r in parag:
                    text += " " + r.strip().replace("\xa0", " ")

                # Retrieving summary on top of articles
                try:
                    summary = tree.xpath("//*[@class='text opener']/p/text()")[
                        0
                    ].strip()
                except:
                    summary = ""

                # Retrieving the section/category from url e.g. http://www.faz.net/aktuell/wirtschaft/unternehmen/vertrieb-von-bio-produkten-etappensieg-von-alnatura-gegen-dm-14567075.html
                if link.startswith("http://www.faz.net"):
                    matchObj = re.match(
                        r"http://www.faz.net/(.*?)/(.*?)/(.*?)/", link, re.M | re.I
                    )
                    if matchObj is not None:
                        try:
                            category = matchObj.group(2)
                        except:
                            category = ""
                        try:
                            sub_category = matchObj.group(3)
                        except:
                            sub_category = ""

                # Retrieving the byline_source/source from url
                try:
                    source = (
                        tree.xpath(
                            "//*[@class='storyTmplBottomNav']//*[@class='quelle']/text()"
                        )[0]
                        .replace("Quelle: ", "")
                        .strip()
                    )
                except:
                    source = ""

                # Retrieving the byline/author
                try:
                    author = (
                        tree.xpath("//*[@class='over ']/small/text()")[0]
                        .replace("Von ", "")
                        .title()
                    )
                except:
                    author = ""

                # Create iso format date
                pub_date = datetime.datetime.strptime(
                    date[5:], "%d %b %Y %H:%M:%S %z"
                ).isoformat()

                # get title
                try:
                    title = tree.xpath("//*[@class='over ']/h1/text()")[0].strip()
                except:
                    title = ""

                tags = []
                if link.startswith("http://plus.faz.net"):
                    tags.append("paid")

                doc = dict(
                    pub_date=pub_date,
                    title=title,
                    text=text.strip(),
                    summary=summary,
                    author=author,
                    source=source,
                    category=category,
                    subcategory=sub_category,
                    url=link,
                    tags=tags,
                )
                doc.update(kwargs)

                yield doc

            else:

                # Retrieving the text of the article. Needs to be done by adding paragraphs together due to structure.
                parag = tree.xpath(
                    "//*[@class='FAZArtikelText']/div[3]/p//text() | //*[@class='FAZArtikelText']/div/p//text()"
                )
                text = ""
                for r in parag:
                    text += " " + r.strip().replace("\xa0", " ")

                # Checking if there are 2 pages and if so, loading the second one and adding its text to the existing string.
                if tree.xpath("boolean(//*[@id='ArticlePagerBottom']/a[2]/@title)"):
                    link2 = tree.xpath("//*[@id='ArticlePagerBottom']/a[2]/@href")[0]
                    req2 = request.Request(link2)
                    read2 = (
                        request.urlopen(req2)
                        .read()
                        .decode(encoding="utf-8", errors="ignore")
                    )
                    tree2 = fromstring(read2)
                    parag2 = tree2.xpath(
                        "//*[@class='FAZArtikelText']/div[3]/p//text()"
                    )
                    for r in parag2:
                        text += " " + r.strip().replace("\xa0", " ")

                # Retrieving summary on top of articles
                try:
                    summary = tree.xpath("//*[@id='artikelEinleitung']/p/text()")[
                        0
                    ].strip()
                except:
                    summary = ""

                # Retrieving the section/category from url e.g. http://www.faz.net/aktuell/wirtschaft/unternehmen/vertrieb-von-bio-produkten-etappensieg-von-alnatura-gegen-dm-14567075.html
                if link.startswith("http://www.faz.net"):
                    matchObj = re.match(
                        r"http://www.faz.net/(.*?)/(.*?)/(.*?)", link, re.M | re.I
                    )
                    if matchObj is not None:
                        try:
                            category = matchObj.group(2)
                        except:
                            category = ""
                        try:
                            sub_category = matchObj.group(3)
                        except:
                            sub_category = ""

                elif link.startswith("http://blogs.faz.net"):
                    catgory = "blog"
                    subcategory = ""

                # Retrieving the byline_source/source from url
                try:
                    source = (
                        tree.xpath(
                            "//*[@class='ArtikelFooter']/p//*[@class='quelle']/text()"
                        )[0]
                        .replace("Quelle: ", "")
                        .strip()
                    )
                except:
                    source = ""

                # Retrieving the byline/author
                try:
                    author = tree.xpath(
                        "//*[@id='artikelEinleitung']//*[@class='Autor']/span/a/span/text()"
                    )[0]
                except:
                    author = ""

                # Create iso format date
                pub_date = datetime.datetime.strptime(
                    date[5:], "%d %b %Y %H:%M:%S %z"
                ).isoformat()

                # get title
                try:
                    title = tree.xpath("//*[@id='artikelEinleitung']/h2/text()")[
                        -1
                    ].strip()
                except:
                    title = ""

                tags = []
                if link.startswith("http://plus.faz.net"):
                    tags.append("paid")

                doc = dict(
                    pub_date=pub_date,
                    title=title,
                    text=text.strip(),
                    summary=summary,
                    author=author,
                    source=source,
                    category=category,
                    subcategory=sub_category,
                    url=link,
                    tags=tags,
                )
                doc.update(kwargs)

                yield doc
