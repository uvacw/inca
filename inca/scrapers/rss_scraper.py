# import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from ..core.scraper_class import UnparsableException
from ..core.database import check_exists
import logging
import feedparser
import re
import requests
from urllib.request import HTTPRedirectHandler
from urllib.request import HTTPCookieProcessor

logger = logging.getLogger("INCA")


def set_cookies(link):
    """
    Set cookies for the request to surpass cookie walls.
    """
    persgroep = [
        "bd.nl",
        "ad.nl",
        "volkskrant.nl",
        "parool.nl",
        "trouw.nl",
        "destentor.nl",
        "gelderlander.nl",
        "ed.nl",
        "bndestem",
        "pzc.nl",
        "tubantia.nl",
    ]
    if "telegraaf.nl" in link:
        link2 = requests.get(link, headers={"User-Agent": "Wget/1.9"}).url
        cookie_url = requests.utils.unquote(link2)
        if "tmgonlinemedia.nl" in cookie_url:
            cookie = re.search("nl/&(.+?)&detect", cookie_url).group(1) + ".essential"
            cookiewall_disable = {"cc2": cookie}
        else:
            cookiewall_disable = {}
    elif any(paper in link for paper in persgroep):
        cookiewall_disable = {"pwv": "2", "pws": "functional"}
    elif "fd.nl" in link:
        cookiewall_disable = {"cookieconsent": "true"}
    elif "nos.nl" in link:
        cookiewall_disable = {
            "Cookie_Consent": "Thu Sep 05 2019 15:04:13 GMT+0200 (Central European Summer Time)"
        }
    elif "metronieuws.nl" in link:
        cookiewall_disable = {"acceptsCookies": "true"}
    elif "geenstijl.nl" in link:
        cookiewall_disable = {"cpc": "10"}
    elif "fok.nl" in link:
        cookiewall_disable = {"cookieok": "1"}
    else:
        cookiewall_disable = {}
    return cookiewall_disable


class MyHTTPRedirectHandler(HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302


cookieprocessor = HTTPCookieProcessor()


class rss(Scraper):
    """
    Reades a generic RSS feed and proceeds if items not already in collection.
    Retrieves full HTML content from link provided in RSS feed
    Yields docs with keys from RSS entry plus full HTML source of linked content.

    Subclasses should probably overwrite the following functions:
        By overwriting the parsehtml function, more keys can be extracted
        By overwriting the getlink function, modifications to the link can be made, e.g. to bypass cookie walls
    """

    def __init__(self):
        Scraper.__init__(self)
        self.doctype = "rss"
        self.version = ".1"
        self.date = datetime.datetime(year=2016, month=8, day=2)

    def get(self, save, **kwargs):
        """Document collected via {} feed reader""".format(self.doctype)

        # This RSS-scraper is a generic fallback option in case we do not have
        # any specific one. Therefore, only use the following generic values
        # if we do not have any more specific info already
        if "rss_url" in kwargs:
            RSS_URL = kwargs["rss_url"]
        else:
            try:
                RSS_URL = self.rss_url
            except:
                RSS_URL = "N/A"

        assert (
            RSS_URL != "N/A"
        ), 'You need to specify the feed URL. Example: rss_url="http://www.nu.nl/rss"'

        if type(RSS_URL) is str:
            RSS_URL = [RSS_URL]

        for thisurl in RSS_URL:
            rss_body = self.get_page_body(thisurl)
            d = feedparser.parse(rss_body)
            for post in d.entries:
                try:
                    _id = post.id
                except:
                    _id = post.link
                if _id == None:
                    _id = post.link
                link = re.sub("/$", "", self.getlink(post.link))
                # By now, we have retrieved the RSS feed. We now have to determine for the item that
                # we are currently processing (post in d.entries), whether we want to follow its
                # link and actually get the full text and process it. If we already have it,
                # we do not need to (therefore check_exists). But also, if we do not want to
                # work with the database backend (as indicated by save=False), we probably also
                # do not want to look something up in the database. We therefore also retrieve it in
                # that case.
                if save == False or check_exists(_id)[0] == False:
                    try:
                        req = requests.get(
                            link,
                            headers={"User-Agent": "Wget/1.9"},
                            cookies=set_cookies(link),
                        )
                        htmlsource = req.text
                    except:
                        htmlsource = None
                        logger.info(
                            "Could not open link - will not retrieve full article, but will give it another try with different User Agent"
                        )
                    # Some (few) scrapers seem to block certain user agents. Therefore, if code above did
                    # not succed, try fetching the article pretending to user Firefox on Windows
                    if not htmlsource or htmlsource == "":
                        try:
                            req = requests.get(
                                link,
                                headers={
                                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                                },
                                cookies=set_cookies(link),
                            )
                            htmlsource = req.text
                        except:
                            htmlsource = None
                            logger.info(
                                "Could not open link - will not retrieve full article"
                            )

                    try:
                        teaser = re.sub(r"\n|\r\|\t", " ", post.description)
                    except:
                        teaser = ""
                    try:
                        datum = datetime.datetime(
                            *feedparser._parse_date(post.published)[:6]
                        )
                    except:
                        try:
                            # alternative date format as used by nos.nl
                            datum = datetime.datetime(
                                *feedparser._parse_date(post.published[5:16])[:6]
                            )
                        except:
                            # print("Couldn't parse publishing date")
                            datum = None
                    doc = {
                        "_id": _id,
                        "title_rss": post.title,
                        "teaser_rss": teaser,
                        "publication_date": datum,
                        "htmlsource": htmlsource,
                        "feedurl": thisurl,
                        "url": re.sub("/$", "", post.link),
                    }
                    if htmlsource is not None:
                        # TODO: CHECK IF PARSEHTML returns None, if so, raise custom exception
                        parsed = self.parsehtml(doc["htmlsource"])
                        if parsed is None or parsed == {}:
                            try:
                                raise UnparsableException
                            except UnparsableException:
                                pass
                        else:
                            doc.update(parsed)
                    parsedurl = self.parseurl(link)
                    doc.update(parsedurl)
                    docnoemptykeys = {k: v for k, v in doc.items() if v or v == False}
                    yield docnoemptykeys

    def get_page_body(self, url, **kwargs):
        """Makes an HTTP request to the given URL and returns a string containing the response body"""
        request = requests.get(url, headers={"User-Agent": "Wget/1.9"})
        response_body = request.text
        return response_body

    def parsehtml(self, htmlsource):
        """
        Parses the html source and extracts more keys that can be added to the doc
        Empty in this generic fallback scraper, should be replaced by more specific scrapers
        """
        return dict()

    def parseurl(self, url):
        """
        Parses the url source and extracts more keys that can be added to the doc
        Empty in this generic fallback scraper, can be replaced by more specific scrapers
        if the URL itself needs to be parsed. Typial use case: The url contains the 
        category of the item, which can be parsed from it using regular expressions
        or .split('/') or similar.
        """
        return dict()

    def getlink(self, link):
        """
        Some sites require some modification of the URL, for example to pass a cookie wall.
        Overwrite this function with a function to do so if neccessary
        """
        return link


if __name__ == "__main__":
    rss().get()
