import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
import logging
import re

logger = logging.getLogger("INCA")


class hostelworld(Scraper):
    """Scrapes Hostelworld reviews"""

    def __init__(self):
        self.BASE_URL = "http://www.hostelworld.com/"

    def get(self, save, maxpages, maxreviewpages, starturl, *args, **kwargs):
        """
        Fetches reviews from hostelworld.com
        maxpage: number of pages with hostels to scrape
        maxreviewpages: number of pages with reviews *per hostel* to scrape
        starturl: URL to first page with hostel results
        """
        self.doctype = "Hostelworld reviews"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=10)

        hostels = []

        page = 1
        current_url = starturl + "?page=" + str(page)
        overview_page = requests.get(current_url)
        first_page_text = ""
        while overview_page.text != first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > maxpages:
                break
            elif page == 1:
                first_page_text = overview_page.text
            tree = fromstring(overview_page.text)

            linkselement = tree.xpath(
                '//*[@class="moreinfo button tiny radius hwta-property-link"]'
            )
            links = [e.attrib["href"] for e in linkselement if "href" in e.attrib]
            names = tree.xpath(
                '//*[@class="resultheader rounded clearfix small-12 medium-7 large-8 columns clearfix"]/h2/a/text()'
            )
            ratings = tree.xpath('//*[@class="hwta-rating-score"]/text()')
            reviewsquantity = tree.xpath('//*[@class="hwta-rating-counter"]/text()')[
                1::2
            ]
            prices = tree.xpath('//*[@class="price"]/text()')
            accommodationtypes = tree.xpath(
                '//*[@class="proptype featureline"]//text()'
            )
            accommodationtypesstrip = [x.strip() for x in accommodationtypes]

            assert (
                len(links)
                == len(names)
                == len(ratings)
                == len(reviewsquantity)
                == len(prices)
                == len(accommodationtypesstrip)
            )

            for i in range(len(links)):
                thishostel = {
                    "name": names[i].strip(),
                    "link": links[i].strip(),
                    "rating": float(ratings[i].strip()),
                    "review_quantity": reviewsquantity[i].strip(),
                    "accommodation_type": accommodationtypesstrip[i],
                }
                hostels.append(thishostel)

            page += 1
            current_url = starturl + "?page=" + str(page)
            overview_page = requests.get(current_url)

        logger.debug(
            "We hebben net alle overzichtspagina's opgehaald. Er zijn {} hostels".format(
                len(hostels)
            )
        )
        # Fetch hostel-specific webpages and enrich the hostel dicts
        hostels_enriched = []
        for hostel in hostels:
            link = hostel["link"]
            logger.debug("ik ga nu {} ophalen".format(link))
            current_page = requests.get(link)
            tree = fromstring(current_page.text)
            try:
                ratingdetail = tree.xpath(
                    '//*[@class="hwta-rating-text-score"]/text()'
                )[0]
            except:
                ratingdetail = ""
            try:
                linkreviews = tree.xpath('//*[@class="review_link"]')
                linkreviewsstrip = [
                    l.attrib["href"] for l in linkreviews if "href" in l.attrib
                ][
                    0
                ]  # assuming that there is only one link
            except:
                linkreviews = ""
                logger.info(
                    "Hostel with link {} did not have any reviews.".format(link)
                )
                thishostel["rating_detail"] = ratingdetail.strip()
                hostels_enriched.append(thishostel)
                continue
            # description, photo's etc.
            thishostel = hostel
            thishostel["rating_detail"] = ratingdetail.strip()
            thishostel["link_reviews"] = linkreviewsstrip
            thishostel["reviews"] = self.getreviews(linkreviewsstrip)
            hostels_enriched.append(thishostel)

        return hostels_enriched

    def getreviews(self, link):
        """
        This function takes a link to a (starting) review page of hostelworld as an input
        and returns all reviews
        """
        base_url = link.rstrip("#propname") + "?showOlderReviews=1&page="
        page = 1
        reviews = []
        while page < maxreviewpages:
            url = base_url + str(page) + "#reviewFilters"
            logger.debug("Processing {}".format(url))
            tree = fromstring(requests.get(url).text)
            reviewtext = tree.xpath('//div[@class="reviewtext translate"]')
            reviewratings = tree.xpath(
                '//div[re:match(@class,"textrating.*")]',
                namespaces={"re": "http://exslt.org/regular-expressions"},
            )
            reviewerdetails = tree.xpath('//li[@class="reviewerdetails"]')
            reviewdate = tree.xpath('//span[@class="reviewdate"]')

            assert (
                len(reviewtext)
                == len(reviewratings)
                == len(reviewerdetails)
                == len(reviewdate)
            )

            if (
                len(reviewtext) == 0
            ):  # we reached the final page, there are no more reviews
                break

            for i in range(len(reviewtext)):
                thisreview = {}
                thisreview["rating"] = reviewratings[i].text_content().strip()
                thisreview["reviewer"] = reviewerdetails[i].text_content().strip()
                thisreview["text"] = reviewtext[i].text_content().strip()
                thisreview["date"] = reviewdate[i].text_content().strip()
                reviews.append(thisreview)

            page += 1

        return reviews


def cleandoc(document):
    for k, v in document.items():
        if type(v) == dict:
            document[k] = cleandoc(v)
        elif type(v) == str:
            if not v.replace("\n", "").replace(" ", ""):
                document[k] = ""
            else:
                document[k] = v
        elif type(v) == str:
            pass

    empty_keys = []
    for k in document.keys():
        if not k.replace("\n", "").replace(" ", "") and not document[k]:
            empty_keys.append(k)
    for k in empty_keys:
        document.pop(k)
    return document
