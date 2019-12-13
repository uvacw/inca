import requests
import datetime
from lxml import html
from ..core.scraper_class import Scraper
from collections import defaultdict


class quotestoscrape(Scraper):

    """A simple example of a scraper. Scrapes quotes.toscrape.com."""

    def __init__(self):

        self.doctype = "quotestoscrape"
        self.START_URL = (
            "http://quotes.toscrape.com/"
        )  # the webpage from where you want to start scraping
        self.version = ".1"
        self.datetime = datetime.datetime(year=2018, month=11, day=7)

    def get(self, save, maxpages, *args, **kwargs):

        """
        Gets quotes from Quotes to Scrape.
        Places them in a dictionary, using author as key.
        maxpages: number of pages to be scraped.    
        """

        quotes = []  # create a list for the scraped quotes
        authors = []  # create a list for the scraped author names
        pageno = 1  # start scraping from page number one

        while pageno <= maxpages:
            current_url = self.START_URL + "page/" + str(pageno) + "/"
            page = requests.get(current_url)
            tree = html.fromstring(page.content)
            quotes.extend(tree.xpath('//span[@class="text"]/text()'))
            authors.extend(tree.xpath('//small[@class="author"]/text()'))
            pageno = pageno + 1
        dictionary = defaultdict(list)
        for k, v in zip(authors, quotes):
            dictionary[k].append(v)

        yield (dictionary)


# Testing:
# from inca import Inca
# from inca.scrapers.groenlinks_scraper import groenlinks
# data = myinca.scrapers.groenlinks(save=False, maxpages = 3, startpage = 1)
# print(data)

# This worked for a while...
# from inca.scrapers.quotestoscrape_scraper import quotestoscrape
# scraping = quotestoscrape()
# data = scraping.get(save  = False, maxpages = 5)
# ... No longer works!

# Now it no longer works (although I didn't change the script?). Instead, this works...
# data = myinca.scrapers.quotestoscrape(save = False, maxpages = 5)
# ...but the output is weird: it yields all other kinds of things as well, not only the dictionary!
# ... no problem, that is added automatically by INCA!
# data[0].keys()
# data[0]["Mother Theresa"]
