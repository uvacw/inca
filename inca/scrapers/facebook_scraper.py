import requests
import datetime
import time
import codecs
from lxml.html import fromstring
from ..core.scraper_class import Scraper
from .rss_scraper import rss
from ..core.database import check_exists
import feedparser
import re
import logging
from selenium import webdriver
from time import sleep
import json


logger = logging.getLogger("INCA")


class facebook(Scraper):
    """Scrapes facebook pages"""

    def __init__(self):

        self.BASE_URL = "https://www.facebook.com/"
        self.START_URL = "https://graph.facebook.com/v2.6/"

    def get(self, save, pagename, app_id, app_secret, maxpages):
        """                                                                     
        Fetches posts from facebook page
        maxpages = number of pages to scrape
	pagename = name of page one wants to scrape
	app_id = individual facebook developer id
	app_secret = individual facebook developer secret
        """
        self.doctype = "facebook"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=10, day=20)

        # retrieve the ID of the facebook page (needed for scraping)
        facebookpage = str(self.BASE_URL + pagename)
        driver = webdriver.Chrome()
        # note: using chrome instead of firefox because of bug in geckodriver that does not allow sending keys
        driver.get("https://findmyfbid.com/")
        searchfield = driver.find_element_by_name("url")
        searchfield.clear()
        searchfield.send_keys(facebookpage)
        driver.find_element_by_xpath("//*[@type ='submit']").click()
        driver.implicitly_wait(5)
        facebook_id = driver.find_element_by_xpath(
            '//*[@id = "success-wrap"]/code'
        ).text
        driver.quit()

        # make access token
        access_token = self.app_id + "|" + self.app_secret

        # construct the first  URL string
        page = 1
        num_posts = 100
        fields = (
            "/posts/?fields=message,link,created_time,type,name,id,"
            + "comments.limit(0).summary(true),shares,reactions"
            + ".limit(0).summary(true)&limit="
        )
        current_url = (
            self.START_URL
            + str(facebook_id)
            + fields
            + str(num_posts)
            + "&access_token="
            + access_token
        )
        posts = []
        has_next_page = True
        first_page_text = ""
        overview_page = requests.get(current_url)
        while has_next_page:
            # retrieve data
            if page > maxpages:
                break
            elif page == 1:
                first_page_text = overview_page.text
            fb_page = json.loads(overview_page.text)
            fb_page1 = fb_page["data"]
            for item in fb_page1:
                try:
                    post_id = item["id"]
                except:
                    post_id = ""
                try:
                    text = item["message"]
                    text = text.replace("\n", "")
                except:
                    text = ""
                try:
                    url = item["link"]
                except:
                    url = ""
                try:
                    post_type = item["type"]
                except:
                    post_type = ""
                try:
                    publication_date = item["created_time"]
                    publication_date = datetime.datetime.strptime(
                        item["created_time"], "%Y-%m-%dT%H:%M:%S+0000"
                    )
                    publication_date = publication_date + datetime.timedelta(
                        hours=-5
                    )  # EST
                except:
                    publication_date = ""
                try:
                    num_reactions = item["reactions"]["summary"]["total_count"]
                except:
                    num_reactions = 0
                try:
                    num_comments = item["reactions"]["summary"]["total_count"]
                except:
                    num_comments = 0
                try:
                    num_shares = item["shares"]["count"]
                except:
                    num_shares = 0

                # get the different reactions to a post (only possible since facebook has different kinds of reactions apart from likes)
                if publication_date.date() > datetime.date(2016, 2, 24):
                    reactions = (
                        "/?fields="
                        "reactions.type(LIKE).limit(0).summary(total_count).as(like)"
                        ",reactions.type(LOVE).limit(0).summary(total_count).as(love)"
                        ",reactions.type(WOW).limit(0).summary(total_count).as(wow)"
                        ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)"
                        ",reactions.type(SAD).limit(0).summary(total_count).as(sad)"
                        ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
                        "&access_token="
                    )
                    current_url = self.START_URL + post_id + reactions + access_token
                    reactions_page = requests.get(current_url)
                    fb_reactions = json.loads(reactions_page.text)
                    try:
                        num_likes = fb_reactions["like"]["summary"]["total_count"]
                    except:
                        num_likes = 0
                    try:
                        num_loves = fb_reactions["love"]["summary"]["total_count"]
                    except:
                        num_loves = 0
                    try:
                        num_wows = fb_reactions["wow"]["summary"]["total_count"]
                    except:
                        num_wows = 0
                    try:
                        num_hahas = fb_reactions["haha"]["summary"]["total_count"]
                    except:
                        num_hahas = 0
                    try:
                        num_sads = fb_reactions["sad"]["summary"]["total_count"]
                    except:
                        num_sads = 0
                    try:
                        num_angrys = fb_reactions["angry"]["summary"]["total_count"]
                    except:
                        num_angrys = 0
                else:
                    num_likes = num_reactions
                    num_loves = 0
                    num_wows = 0
                    num_hahas = 0
                    num_sads = 0
                    num_angrys = 0

                posts.append(
                    {
                        "text": text,
                        "post_id": post_id,
                        "publication_date": publication_date,
                        "url": url,
                        "category": post_type,
                        "reactions_int": num_reactions,
                        "comments_int": num_comments,
                        "shares_int": num_shares,
                        "likes_int": num_likes,
                        "loves_int": num_loves,
                        "hahas_int": num_hahas,
                        "wows_int": num_wows,
                        "sads_int": num_sads,
                        "angrys_int": num_angrys,
                        "pagename": pagename,
                    }
                )
            page += 1

            if "paging" in fb_page.keys():
                current_url = fb_page["paging"]["next"]
            else:
                has_next_page = False
            overview_page = requests.get(current_url)
        return posts
