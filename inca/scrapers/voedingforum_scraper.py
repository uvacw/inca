import requests
import datetime
from lxml.html import fromstring
from ..core.scraper_class import Scraper
import logging
import re
from time import sleep
from random import randrange
import re

logger = logging.getLogger("INCA")

logger.setLevel("DEBUG")


# Multipage non-rss scraper. When a non-existing URL is requested we get an error messages. The loop stops when the error message is encountered.
class voedingsforum(Scraper):
    def __init__(self):

        self.START_URL = "http://www.voedingsforum.nl/"
        self.BASE_URL = "http://www.voedingsforum.nl/"

    def get(self, save, maxfora, forumid, maxthreads, maxpages, *args, **kwargs):
        """                                                                     
        Fetches articles from Voedingsforum
        maxfora = maximum number of forums to scrape
        forumid = ID of forum 
        maxthreads = maximum number of threads in each forum to scrape
        maxpages = maximum number of pages in each thread to scrape
        """
        self.doctype = "voedingsforum (health)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=12, day=15)

        allfora = []

        current_url = self.START_URL
        # you are redirected to a cookiewall _unless_ a cookie with the key cookieAccept and the value is True is send to the server
        # we found that out by inspecting the source code of the cookiewall page to which we were redirected: we examined the javascript-code in there, and the central functionality seemed to be that it created such a cookie.
        # We can do so manually by simply providing a python dict:
        overview_page = requests.get(current_url, cookies={"cookieAccept": "True"})
        tree = fromstring(overview_page.text)
        linkobjects = tree.xpath("//table//b/a")
        links = [
            self.BASE_URL + l.attrib["href"] for l in linkobjects if "href" in l.attrib
        ]
        links = links[0:maxfora]

        if forumid:
            links = [
                "http://www.voedingsforum.nl/forum.asp?FORUM_ID={}".format(self.FORUMID)
            ]

        logger.debug(
            "There are {} subforums in total in the Voedingsforum, and they are:".format(
                len(links)
            )
        )
        logger.debug("\n".join(links))
        it = 0
        for link in links:
            currentforum = {}
            currentforum["url"] = link
            treetitles = tree.xpath("//table//b/a/@title")
            forumtitle = treetitles[it]
            currentforum["name"] = forumtitle
            currentforum["threads"] = []
            page = 1
            current_page = link
            sleep(randrange(5, 10))
            overview_pagesub = requests.get(
                current_page, cookies={"cookieAccept": "True"}
            )
            logger.debug("now fetching this subforum {}".format(link))
            # The loop stops by checking whether the next page contains the following text.
            while (
                overview_pagesub.content.find(
                    b"Foutmelding" and b"Geen onderwerpen gevonden"
                )
                == -1
            ):
                logger.debug("this subforum does not contain error messages")
                tree_sub = fromstring(overview_pagesub.text)
                sublinkobjects = tree_sub.xpath(
                    "//table//table//tr/td/a[not(@onmouseout)]/@href"
                )
                logger.debug(
                    "this subforum has {} threads, and they are:".format(
                        len(sublinkobjects)
                    )
                )
                sublinks = [self.BASE_URL + li for li in sublinkobjects]
                logger.debug("\n".join(sublinks))
                tt = 0
                for sublink in sublinks:
                    currentthread = {}
                    treethreadtitles = tree_sub.xpath(
                        '//td[@class="forumcellcolor"]//a/text()'
                    )
                    threadtitles = [t for t in treethreadtitles if t.isdigit() == False]
                    threadtitle = threadtitles[tt]
                    currentthread["titlethread"] = threadtitle
                    treethreadread = tree_sub.xpath(
                        '//td[@class="forumdark"]/font[@size="2"]/node()'
                    )
                    threadreadclean = [int(t) for t in treethreadread if int(t) > 1]
                    currentthread["timesread"] = threadreadclean[tt]
                    currentthread["posts"] = []
                    pagesub = 1
                    logger.debug("fetching now the following thread {}".format(sublink))
                    sleep(randrange(5, 10))
                    this_page = requests.get(sublink)
                    while True:
                        treesub = fromstring(this_page.text)
                        thread = treesub.xpath('//table//span[@id="msg"]')
                        messages = [t.text_content() for t in thread]
                        messages = [b.strip() for b in messages]
                        postlist = []
                        for message in messages:
                            if len(message) > 0 and message.find("adsbygoogle") == -1:
                                postlist.append({"post": message})
                        # User information - extracting from the elements. Username and level come together in one list, country of origin and amount of messages in a second list

                        user_elem = treesub.xpath(
                            '//*[@class="topiclight" or @class="topicdark"]'
                        )

                        if len(
                            [True for u in user_elem if len(u.getchildren()) == 2]
                        ) != len(postlist):
                            logger.warning(
                                "OOOPS! We found a different number of posts and users. That seems wrong, but we cannot solve it. We are going to skip the entire page"
                            )

                        else:  # only if we are sure that we have lists of equal length, we are going to anayze this page
                            ii = 0

                            for user in user_elem:
                                userinfo = user.getchildren()
                                if len(userinfo) == 2:
                                    userlevel = userinfo[0].text_content()
                                    postlist[ii]["username"] = userlevel.split()[0]
                                    postlist[ii]["userlevel"] = userlevel.split()[1]

                                    countryamount = (
                                        userinfo[1]
                                        .text_content()
                                        .replace("Berichten", " ")
                                        .replace("\r\n", " ")
                                        .replace("\t\t", "")
                                        .replace("                  ", " ")
                                        .replace("   ", " ")
                                    )

                                    thiscountrystring = "".join(
                                        re.findall(r"[A-Za-z]", countryamount)
                                    )
                                    if thiscountrystring == "":
                                        postlist[ii]["usercountry"] = "NA"
                                    else:
                                        postlist[ii]["usercountry"] = thiscountrystring

                                    postlist[ii]["useramountofposts"] = int(
                                        "".join(re.findall(r"[0-9]", countryamount))
                                    )
                                    ii += 1

                                else:
                                    continue

                        pagesub += 1
                        if pagesub > maxthreads:
                            break
                        next_url = sublink + "&whichpage=" + str(pagesub)
                        sleep(randrange(5, 10))
                        next_page = requests.get(next_url)
                        logger.debug(
                            "fetching now the next page of the thread {}".format(
                                next_url
                            )
                        )
                        if next_page.content.find(b"/_lib/img/icon_user_profile") == -1:
                            logger.debug(
                                "this thread has only one page, continuing to next thread"
                            )
                            break
                        else:
                            this_page = next_page
                    currentthread["posts"] = postlist

                    currentforum["threads"].append(currentthread)
                    tt += 1
                page += 1
                if page > maxpages:
                    break
                current_page = (
                    link + "&sortfield=lastpost&sortorder=desc&whichpage=" + str(page)
                )
                sleep(randrange(5, 10))
                overview_pagesub = requests.get(current_page)
                logger.debug(
                    "fetching now the next page of the subforum {}".format(current_page)
                )

            allfora.append(currentforum)
            it += 1

        return allfora
