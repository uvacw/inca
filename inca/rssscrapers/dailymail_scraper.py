from lxml import html
from urllib import request
from lxml.html import fromstring
from inca.scrapers.rss_scraper import rss
from inca.core.scraper_class import Scraper
import re
import feedparser
import logging
import datetime
import requests
from lxml import etree

logger = logging.getLogger("INCA")


class dailymail(rss):
    """Scrapes dailymail.co.uk """

    def __init__(self):
        self.doctype = "dailymail (www)"
        self.rss_url = "http://www.dailymail.co.uk/articles.rss"
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
        req = request.Request("http://www.dailymail.co.uk/articles.rss")
        read = request.urlopen(req).read().decode(encoding="utf-8", errors="ignore")
        tree = etree.fromstring(read)
        article_urls = tree.xpath("//channel//item//link/text()")
        descriptions = tree.xpath("//channel//item//description/text()")
        dates = tree.xpath("//channel//item//pubDate/text()")
        titles = tree.xpath("//channel//item//title/text()")

        for link, title, date in zip(
            article_urls, titles, dates
        ):  # you go to each article page
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
            parag = tree.xpath(
                "//div[@itemprop='articleBody']/p//text() | //*[@class='mol-para-with-font']/font/text() | //*[@class='mol-para-with-font']/font/span/text()"
            )
            text = ""
            for r in parag:
                text += " " + r.strip()
                # adding a space at the end of the paragraph.

            # Retrieving bullet points on top of articles
            bullet = tree.xpath(
                "//*[@class='mol-bullets-with-font']/li/font/strong/text()"
            )

            # Retrieving the section/category from url
            matchObj = re.match(
                r"http://www.dailymail.co.uk/(.*?)/(.*?)/", link, re.M | re.I
            )
            category = matchObj.group(1)

            # Retrieving the byline_source/source from url
            if matchObj.group(1) == "wires":
                byline_source = matchObj.group(2)
            else:
                byline_source = ""

            # Retrieving the byline/author
            byline_tree = tree.xpath("//*[@class='author']/text()")

            # Eliminating anything coming after "for" as in many cases it says "For Mailonline", "For dailymail" etc.
            myreg = re.match("(.*?)( [f|F]or )", ", ".join(byline_tree), re.M | re.I)
            if myreg is None:
                author_list = byline_tree
            else:
                author_list = myreg.group(1).split(",")

            # Create iso format date
            try:
                pub_date = datetime.datetime.strptime(
                    date[5:], "%d %b %Y %H:%M:%S %z"
                ).isoformat()
            except:
                pub_date = ""

            # somehow the rss title contains some \n
            title = title.strip()

            doc = dict(
                pub_date=pub_date,
                title=title,
                text=text,
                bullet=bullet[0] if bullet else "",
                author=author_list,
                source=byline_source,
                category=category,
                url=link,
            )
            doc.update(kwargs)
            yield doc
