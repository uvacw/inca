import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange
import urllib.request as urllib2

logger = logging.getLogger("INCA")
logger.setLevel(logging.DEBUG)


class tripadvisor(Scraper):
    """Scrapes Tripadvisor reviews"""

    def __init__(
        self,
        startpage=1,
        maxpages=2,
        maxreviewpages=5,
        maxurls=50,
        starturl="https://www.tripadvisor.com/Hotels-g188590-Amsterdam_North_Holland_Province-Hotels.html",
    ):
        """
        startpage: the overviewpage where to start scraping
        maxpages: number of overviewpages with hotels to scrape at one time
        maxreviewpages: number of pages with reviews per hotel to scrape
        starturl: URL to first overviewpage (the startpage of a city)
        maxurl: number of overview pages that are made of the starturl (always set larger than maxpages)
        """

        self.START_URL = starturl
        self.BASE_URL = "http://www.tripadvisor.com"
        self.MAXPAGES = maxpages
        self.STARTPAGE = startpage
        self.MAXREVIEWPAGES = maxreviewpages
        self.MAXURLS = maxurls
        self.BLACKLIST = (
            []
        )  # review pages that never should be fetched (e.g. because they do not conform with the standard layout)

    def get(self):
        """Fetches reviews from Tripadvisor.com"""
        self.doctype = "tripadvisor_hotel"
        self.version = ".1"
        self.date = datetime.datetime(year=2018, month=1, day=24)

        hotels = []
        allurls = []

        # Creating the correct url for creating following overviewpages, by altering the starturl
        starturl_altering = self.START_URL + "#BODYCON"
        occur = 2
        indices = [x.start() for x in re.finditer("-", starturl_altering)]
        part1 = starturl_altering[0 : indices[occur - 1]]
        part2 = starturl_altering[indices[occur - 1] + 1 :]
        starturl = part1 + "-oa{}-" + part2
        logger.debug(
            "This scraper is scraping information from the following Tripadvisor list of hotels: {}".format(
                starturl
            )
        )

        # Possible urls are created, but the list can't be longer than the maxpages defined above
        for i in range(self.STARTPAGE * 30, self.MAXURLS * 30, 30):
            allurls.append(starturl.format(i))
        if len(allurls) > self.MAXPAGES:
            allurlsgen = (e for e in allurls[: int(self.MAXPAGES)])
            logger.debug(
                "The list of created URLs is longer than the defined max overviewpages. In total, {} page(s) are being scraped".format(
                    self.MAXPAGES
                )
            )
        else:
            allurlsgen = (e for e in allurls)
            logger.debug(
                "The list of created URLs is shorter than the defined max overviewpages. In total, {} page(s) are being scraped".format(
                    len(allurls)
                )
            )
        thisurl = next(allurlsgen)
        sleep(randrange(5, 10))
        req = urllib2.Request(
            thisurl,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
            },
        )
        htmlsource = (
            urllib2.urlopen(req).read().decode(encoding="utf-8", errors="ignore")
        )
        logger.debug("Fetched the following overviewpage: {}".format(thisurl))
        page = 1
        while True:
            # while htmlsource.find('prw_rup prw_meta_hsx_three_col_listing')!=-1:
            tree = fromstring(htmlsource)
            if tree.xpath('//*[@class="pageNum first current "]') and page > 1:
                logger.debug("OOPS, WE ARE BACK AT THE FIRST PAGE AGAIN!")
                break
            logger.debug("This page has pagenumber {}".format(page))

            linkselement = tree.xpath(
                '//*[@class="relWrap"]//*[@class="property_title prominent"]'
            )
            links = [
                "http://www.tripadvisor.com" + e.attrib["href"]
                for e in linkselement
                if "href" in e.attrib
            ]
            names = tree.xpath(
                '//*[@class="relWrap"]//*[@class="property_title prominent"]/text()'
            )
            reviewsquantity = tree.xpath('//*[@class="review_count"]//text()')

            assert len(links) == len(names) == len(reviewsquantity)
            logger.debug(
                "This overviewpage has {} links to hotels, {} hotel names and {} review quantities".format(
                    len(links), len(names), len(reviewsquantity)
                )
            )

            for hotel in range(len(links)):
                thishotel = {
                    "name": names[hotel].strip(),
                    "link": links[hotel].strip(),
                    "reviewquantity": reviewsquantity[hotel].strip(),
                    "reviews": [],
                }
                hotels.append(thishotel)

            # apart from the initial while-loop condition, we also stop the loop once we reach
            # the maximum number of pages defined before:
            try:
                next_url = next(allurlsgen)
            except StopIteration:
                break
            sleep(randrange(5, 10))
            req = urllib2.Request(
                next_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                },
            )
            htmlsource = (
                urllib2.urlopen(req).read().decode(encoding="utf-8", errors="ignore")
            )
            logger.debug("Fetched the following overviewpage: {}".format(next_url))
            page += 1
        logger.debug(
            "We have fetched all overviewpages that exist (or the max number of pages defined). There are {} hotels in total.".format(
                len(hotels)
            )
        )

        # Fetch hotel-specific webpages and enrich the hotel dicts
        for hotel in hotels:
            link = hotel["link"]
            logger.debug("Fetched the hotel-specific webpage: {}".format(link))
            logger.debug(
                "This is all the info we already have about the hotel: {}.".format(
                    hotel
                )
            )
            sleep(randrange(5, 10))

            if link not in self.BLACKLIST:
                logger.debug("This page is not in the blacklist, and is being scraped")
                req = urllib2.Request(
                    link,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                    },
                )
                htmlsource = (
                    urllib2.urlopen(req)
                    .read()
                    .decode(encoding="utf-8", errors="ignore")
                )
                tree = fromstring(htmlsource)
                try:
                    overallrating = tree.xpath('//*[@class="overallRating"]/text()')[0]
                    logger.debug(
                        "This hotel has an overall rating of {}.".format(overallrating)
                    )
                except:
                    ""
                    logger.info(
                        "Hotel with link {} did not have an overall rating.".format(
                            link
                        )
                    )
                try:
                    ranking = "".join(
                        tree.xpath(
                            '//*[@class="header_popularity popIndexValidation"]/a/text() | //*[@class="header_popularity popIndexValidation"]/b/text() | //*[@class="header_popularity popIndexValidation"]/text()'
                        )
                    )
                    logger.debug("This hotel has a ranking of {}.".format(ranking))
                except:
                    ""
                    logger.info(
                        "Hotel with link {} did not have a ranking.".format(link)
                    )

                thishotel = hotel
                thishotel["ranking"] = ranking.strip()
                try:
                    thishotel["overall_rating"] = float(overallrating.strip())
                except:
                    thishotel["overall_rating"] = overallrating.strip()
            else:
                logger.debug(
                    "This link was not fetched since it is on the blacklist: {}".format(
                        link
                    )
                )
                continue

            # Fetch hotel-specific reviews and enrich the hotel dicts
            reviews_thishotel = []

            # The hotel-specific webpage shows the reviews, but only with limited text
            # so we go to the link of the first review which will give an extended list of all reviews
            linkelement_reviewpage = tree.xpath(
                '//*[@class="quote isNew"]/a | //*[@class="quote"]/a'
            )
            link_reviewpage = [
                e.attrib["href"] for e in linkelement_reviewpage if "href" in e.attrib
            ][0]
            reviews_thisurl = self.BASE_URL + link_reviewpage

            # We check how many pages with reviews there are, for this we only need the first review page of the hotel
            req = urllib2.Request(
                reviews_thisurl,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                },
            )
            htmlsource = (
                urllib2.urlopen(req).read().decode(encoding="utf-8", errors="ignore")
            )
            tree = fromstring(htmlsource)
            try:
                maxpages = int(
                    tree.xpath('//*[@class="pageNum last taLnk "]/text()')[0]
                )
            except:
                maxpages = int(1)
            logger.debug("There seem to be {} page(s) with reviews.".format(maxpages))

            # but if these are more than our maximum set above, we only take so much
            if maxpages > self.MAXREVIEWPAGES:
                logger.debug(
                    "However, we are only going to scrape {}.".format(
                        self.MAXREVIEWPAGES
                    )
                )
                maxpages = self.MAXREVIEWPAGES
            if maxpages < self.MAXREVIEWPAGES:
                logger.debug("So we are going to scrape {} pages.".format(maxpages))

            numberofpage = 1
            while True:
                sleep(randrange(5, 10))
                req = urllib2.Request(
                    reviews_thisurl,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                    },
                )
                htmlsource = (
                    urllib2.urlopen(req)
                    .read()
                    .decode(encoding="utf-8", errors="ignore")
                )
                logger.debug(
                    "Fetched the hotel-specific review webpage: {}.".format(
                        reviews_thisurl
                    )
                )
                tree = fromstring(htmlsource)
                logger.debug("The number of the page is {}.".format(numberofpage))
                totalreviews = tree.xpath(
                    '//*[@class="innerBubble"]/div[@class="wrap"]'
                )  # tree.xpath('//*[@class="wrap"]')

                # Check if the elements that were gathered in 'totalreviews' above are actual reviews
                allreviews = []
                for every_review in totalreviews:
                    for subelement in every_review.getchildren():
                        if (
                            "prw_rup prw_reviews_text_summary_hsx"
                            in subelement.values()
                        ):
                            allreviews.append(every_review)
                logger.debug(
                    "There are {} reviews being processed".format(len(allreviews))
                )
                if len(allreviews) != len(totalreviews):
                    logger.error(
                        "OOPS, there were more review elements than actual reviews! This is the current link {}. There are {} review elements that were not reviews.".format(
                            reviews_thisurl, len(totalreviews) - len(allreviews)
                        )
                    )
                totalpages = tree.xpath('//*[@class="pageNum last taLnk "]/text()')
                if len(allreviews) < 7:
                    if totalpages == []:
                        logger.debug(
                            "This page contains less than 7 reviews, however, it is the last reviewpage, so this makes sense."
                        )
                    else:
                        logger.debug(
                            "OOPS, this page contains less than 7 review elements! The htmlsource is saved under 'debugpage:date' and the reviews are printed below:"
                        )
                        for debugreview in allreviews:
                            logger.error(debugreview.text_content())
                        with open(
                            "debugpage-{}.html".format(datetime.datetime.now()),
                            mode="w",
                        ) as fo:
                            fo.write(htmlsource)
                if len(allreviews) > 7:
                    logger.error(
                        "OOPS, this page contains MORE than 7 review elements! The htmlsource is saved under 'debugpage:date' and this page is skipped"
                    )
                    with open(
                        "debugpage-{}.html".format(datetime.datetime.now()), mode="w"
                    ) as fo:
                        fo.write(htmlsource)
                    continue
                if allreviews == []:
                    logger.error(
                        "OOPS, this page contains no reviews at all. The htmlsource is saved under 'debugpage:date' and this page is skipped"
                    )

                reviews = []
                for review in allreviews:
                    thisreview = {}
                    for element in review.getchildren():
                        if "quote isNew" in element.values():
                            thisreview["headline"] = element.text_content().strip()
                        if "quote" in element.values():
                            thisreview["headline"] = element.text_content().strip()
                        if "prw_rup prw_reviews_text_summary_hsx" in element.values():
                            thisreview["review"] = element.text_content().strip()
                            if thisreview["review"] == "":
                                thisreview["review"] = "UNRETRIEVABLE REVIEW"
                        if "rating reviewItemInline" in element.values():
                            date = element.getchildren()[1].attrib["title"].strip()
                            thisreview["date"] = date
                            infodate = element.text_content().strip()
                            splitat_mobile = infodate.find("via mobile")
                            if splitat_mobile > -1:
                                thisreview["mobile"] = True
                            else:
                                thisreview["mobile"] = False
                            ratingelement = int(
                                element.getchildren()[0]
                                .attrib["class"]
                                .lstrip("ui_bubble_rating bubble_")
                                .replace("0", "")
                            )
                            thisreview["rating"] = ratingelement
                        if "mgrRspnInline" in element.values():
                            response_elements = element.getchildren()
                            for response_element in response_elements:
                                if (
                                    "prw_rup prw_reviews_response_header"
                                    in response_element.values()
                                ):
                                    thisreview["response_date"] = (
                                        response_element.getchildren()[0]
                                        .getchildren()[0]
                                        .text_content()
                                    )
                                    responder = response_element.getchildren()[
                                        0
                                    ].text_content()
                                    splitat_responder = responder.find(", responded")
                                    thisreview["responder"] = responder[
                                        :splitat_responder
                                    ]
                                if (
                                    "prw_rup prw_reviews_text_summary_hsx"
                                    in response_element.values()
                                ):
                                    thisreview[
                                        "response"
                                    ] = response_element.text_content()
                            if thisreview["response"] == "":
                                thisreview["response"] = "UNRETRIEVABLE RESPONSE"
                        else:
                            thisreview["response"] = "NA"
                        if (
                            "prw_rup prw_reviews_category_ratings_hsx"
                            in element.values()
                        ):
                            notravelinfo = element.getchildren()[0].text_content()
                            if notravelinfo == "":
                                thisreview["date_of_stay"] = "NA"
                            else:
                                travelinfo = (
                                    element.getchildren()[0]
                                    .getchildren()[0]
                                    .getchildren()[0]
                                    .getchildren()
                                )
                                if len(travelinfo) == 1:
                                    aboutstay = (
                                        element.getchildren()[0]
                                        .getchildren()[0]
                                        .getchildren()[0]
                                        .text_content()
                                    )
                                else:
                                    aboutstay = travelinfo[0].text_content()
                                    firstratings = travelinfo[1].text_content()
                                    splitat_stay = aboutstay.find("traveled")
                                    if splitat_stay == -1:
                                        thisreview["date_of_stay"] = aboutstay.replace(
                                            "Stayed: ", ""
                                        ).strip()
                                    else:
                                        dateofstay, travelcompany = (
                                            aboutstay[: splitat_stay - 2],
                                            aboutstay[splitat_stay:],
                                        )
                                        thisreview[
                                            "date_of_stay"
                                        ] = dateofstay.strip().replace("Stayed: ", "")
                                        thisreview[
                                            "travel_company"
                                        ] = travelcompany.strip()
                    logger.debug(
                        "For this review, the following information was found: {}.".format(
                            thisreview.keys()
                        )
                    )
                    reviews.append(thisreview)
                logger.debug("This page has {} reviews in total".format(len(reviews)))

                review_usernames = []
                review_locations = []
                review_contributions = []
                review_votes = []
                bios = tree.xpath('//*[@class="member_info"]')
                for b in bios:
                    allinfo = b.getchildren()
                    if b.getchildren()[0].text_content() == "":
                        review_usernames.append(b.getchildren()[1].text_content())
                        review_locations.append("NA")
                    else:
                        relevantinfo = allinfo[0].getchildren()
                        review_usernames.append(relevantinfo[1].text_content())
                        if len(relevantinfo) == 3:
                            review_locations.append(relevantinfo[2].text_content())
                        else:
                            review_locations.append("NA")
                    userinfo = allinfo[0].getchildren()
                    userhistory_elements = allinfo[1].getchildren()
                    userhistory = userhistory_elements[0].getchildren()
                    if len(userhistory) == 4:
                        review_contributions.append(int(userhistory[1].text_content()))
                        review_votes.append(int(userhistory[3].text_content()))
                    elif len(userhistory) == 2:
                        review_contributions.append(int(userhistory[1].text_content()))
                        review_votes.append(
                            None
                        )  # cannot be a string as we expect a number
                    else:
                        review_contributions.append(
                            None
                        )  # as this field usually contains ints, we cannot add the string 'NA'
                        review_votes.append(
                            None
                        )  # cannot be a string as we expect a number
                logger.debug(
                    "This page has a list with {} user contributions.".format(
                        len(review_contributions)
                    )
                )
                logger.debug(
                    "This page has a list with {} user votes.".format(len(review_votes))
                )
                logger.debug(
                    "This page has a list with {} user locations.".format(
                        len(review_locations)
                    )
                )
                logger.debug(
                    "This page has a list with {} usernames.".format(
                        len(review_usernames)
                    )
                )

                review_images = []
                everyreview = tree.xpath('//*[@class="innerBubble"]/div[@class="wrap"]')
                for r in everyreview:
                    if r.find("*//noscript/img") is not None:
                        review_images.append(
                            [
                                {"url": e.attrib["src"]}
                                for e in r.findall("*//noscript/img")
                            ]
                        )
                    else:
                        review_images.append([])
                logger.debug(
                    "This page has a list with {} images".format(len(review_images))
                )

                review_moreratings = []
                for r in everyreview:
                    allratings = {}
                    review_ratingthing = []
                    review_ratingvalue = []
                    review_allratings = r.findall("*//li")[1:]
                    for rating in review_allratings:
                        review_ratingthing.append(rating.text_content())
                        review_ratingvalue.append(rating[0].items()[0][1][-2:])
                        assert len(review_ratingthing) == len(review_ratingvalue)
                        allratings = dict(zip(review_ratingthing, review_ratingvalue))
                    review_moreratings.append(allratings)
                logger.debug(
                    "This page has a list with {} specific ratings (e.g. staff/cleanliness)".format(
                        len(review_moreratings)
                    )
                )

                review_is_sponsored = []
                for review in everyreview:
                    is_sponsored = (
                        review.text_content().find(
                            "Review collected in partnership with"
                        )
                        > -1
                    )
                    review_is_sponsored.append(is_sponsored)
                logger.debug(
                    "This page has a list with {} review sponsorships".format(
                        len(review_is_sponsored)
                    )
                )

                assert (
                    len(review_usernames)
                    == len(review_locations)
                    == len(review_votes)
                    == len(review_contributions)
                    == len(review_images)
                    == len(review_moreratings)
                    == len(review_is_sponsored)
                    == len(reviews)
                )
                logger.debug("All lists have the same length")
                i = 0
                for r in reviews:
                    r.update(
                        {
                            "username": review_usernames[i].strip(),
                            "location": review_locations[i],
                            "votes": review_votes[i],
                            "contributions": review_contributions[i],
                            "images": review_images[i],
                            "specific_ratings": review_moreratings[i],
                            "partnership": review_is_sponsored[i],
                        }
                    )
                    i += 1
                logger.debug("All lists have been added as keys to the dict")
                thishotel["reviews"] += reviews
                logger.debug("The reviews have been added to the hotel")

                # go to the next page, unless there is no next page
                next_reviewpageelement = tree.xpath('//*[@class="nav next taLnk "]')
                if next_reviewpageelement == []:
                    logger.debug(
                        "There is no next page after the current page, so we're breaking"
                    )
                    break
                else:
                    next_pagelink = [
                        e.attrib["href"]
                        for e in next_reviewpageelement
                        if "href" in e.attrib
                    ][0]
                    reviews_thisurl = self.BASE_URL + next_pagelink
                    logger.debug("The next page is: {}".format(reviews_thisurl))

                if numberofpage >= maxpages:
                    logger.debug(
                        "The page number is above the max number of pages we are scraping, so we stop"
                    )
                    break
                numberofpage += 1
            yield thishotel
