from ..core.client_class import Client, elasticsearch_required
from ..core.basic_utils import dotkeys
from ..core.search_utils import doctype_first

import logging
import json
import httplib2
import requests
from requests import ConnectionError, ConnectTimeout
import oauth2client
from oauth2client import client
from oauth2client.client import Credentials
from urllib.parse import urlencode

logger = logging.getLogger("INCA.%s" % __name__)


class youtube(Client):
    """Class to add youtube credentials """

    service_name = "youtube"
    timeout = 100

    def _standardize_id(self, item):
        if type(item["id"]) == dict:
            item["youtube_id"] = item["id"]
            item["id"] = item["id"].get("videoId", "")
        elif type(item["id"]) == str:
            item["youtube_id"] = {"videoId": item["id"]}
        return item

    @elasticsearch_required
    def add_application(self, appname="default", response=None):
        """add a youtube app to generate credentials"""
        if not response:

            app_prompt = {
                "header": "Create a Youtube Application",
                "description": "You will need a YouTube app to start collecting data \n"
                "from the YouTube service. You can create it by following these steps: \n"
                "\n"
                "1.  Go to https://console.developers.google.com/ \n"
                "2.  Click on 'view all' and search for 'YouTube Data API v3' \n"
                "3.  If necessary, agree with the Terms of service \n"
                "4.  Create a project with an arbitrary name (if you do not already have one) \n"
                "5.  Click on 'Enable' \n"
                "6.  Click on 'Create Credentials', the blue button on the rigth side of the screen \n"
                "7.  For 'Which API are you using, keep the 'YouTube API v3 option' \n"
                "    For 'Where will you be calling the API from?' pick 'Other UI (e.g. Windows, CLI tool)' \n"
                "    For 'Which data will you be accessing', you can should pick 'User data' \n"
                "8.  Click 'What credentials do I need?' \n"
                "9.  Create an arbitrary name for your OAuth 2.0 client ID \n"
                "10. Click 'Done'. (You do not have to download the credentials yet.) \n"
                "11. Click on 'Create credentials', and choose 'API key'.",
                "inputs": [
                    {
                        "label": "Application name",
                        "description": "An internal identifier for your app. You can give your app any name ",
                        "help": "The application name does not have to match that of the YouTube app",
                        "input_type": "text",
                        "minimum": 4,
                        "maximum": 15,
                        "default": appname,
                    },
                    {
                        "label": "Application API key",
                        "description": "\nPlease copy the API key in the tab Credentials ",
                        "help": "The API key should look something like 'AIzaSyCTeyFOP6iNQ_d5ceG9sXbbheLmccz5ETk'",
                        "input_type": "text",
                        "minimum": 8,
                        "maximum": 100,
                    },
                    {
                        "label": "Application Client Id",
                        "description": "\nPlease copy the Client ID shown under 'OAuth 2.0 client IDs' in the tab Credentials ",
                        "help": "The credentials should look something like '708587097539-gbpoflpng1ola0hbh4fcob3ugL1Dcy60.apps.googleusercontent.com'",
                        "input_type": "text",
                        "minimum": 8,
                        "maximum": 100,
                    },
                    {
                        "label": "Application Client Secret",
                        "description": "\nPlease copy the Client secret shown under 'OAuth 2.0 client Ids' in the tab Credentials. Make sure you do not copy the space behind the code ",
                        "help": "The credentials should look something like 'AIzaWyBcVB4AB9zMF9LQbghB3yF5z13Tp'",
                        "input_type": "text",
                        "minimum": 8,
                        "maximum": 50,
                    },
                    {
                        "label": "Now activate credential additions for your application",
                        "description": "In the 'credentials' tab of the Google API overview click on 'OAuth consent screen'. Here, you should fill in an email address and appname to be shown to users when adding credentials. Once you have entered this information, click 'Save' \nNow press enter to finish creating your app",
                        "help": "only the email and product name are required",
                        "input_type": "bool",
                        "default": "True",
                    },
                ],
            }

            response = self.prompt(app_prompt)
            return self.add_application(appname=appname, response=response)

        elif response:
            credentials = {
                "client_id": response["Application Client Id"],
                "client_secret": response["Application Client Secret"],
            }
            return self.store_application(
                appname=response["Application name"], app_credentials=credentials
            )

    @elasticsearch_required
    def add_credentials(self, appname="default"):
        """Add credentials for an app"""
        retrieved_app = self.load_application(app=appname)
        saved_app = retrieved_app["_source"]["credentials"]
        flow = oauth2client.client.OAuth2WebServerFlow(
            client_id=saved_app["client_id"],
            client_secret=saved_app["client_secret"],
            scope="https://www.googleapis.com/auth/youtube.force-ssl",
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        )
        app_url = flow.step1_get_authorize_url()
        credentials_prompt = {
            "header": "add credentials to app {appname}".format(**locals()),
            "description": "Go to the below URL, select the account you want to add to this app [{appname}] and click 'Allow'\n\nUrl: {app_url}".format(
                **locals()
            ),
            "inputs": [
                {
                    "label": "Credentials ID",
                    "description": "This is an internal identifier for these credentials. You can give them any name. ",
                    "help": "",
                    "input_type": "text",
                    "minimum": 3,
                    "maximum": 20,
                },
                {
                    "label": "Authentication code",
                    "description": "Please enter the authentication code from the webpage:",
                    "help": "",
                    "input_type": "text",
                    "minimum": 10,
                },
            ],
        }
        response = self.prompt(credentials_prompt)
        credentials = flow.step2_exchange(response["Authentication code"])

        return self.store_credentials(
            app=appname,
            credentials=credentials.to_json(),
            id=response["Credentials ID"],
        )

    def _get(
        self,
        url,
        params=None,
        data=None,
        retries=3,
        timeout=20,
        oauth=True,
        ignore_errors=False,
    ):
        """
        This function wraps requests.get to handle the YouTube API specific error codes that may pop up.
        """

        third_party_warning = (
            "might not have enabled third-party contributions for this caption"
        )

        try:
            if oauth:
                http_auth = self._credentials["_source"]["credentials"]
                credentials = oauth2client.client.GoogleCredentials.from_json(http_auth)
                http = httplib2.Http()
                http = credentials.authorize(http)
                params = params and "?" + urlencode(params) or ""
                response = http.request(
                    url + "{params}".format(params=params), "GET", body=data
                )

                if type(response) == tuple and response[0]["status"] == "200":
                    try:
                        res = json.loads(response[1].decode("utf-8", "ignore"))
                    except ValueError:
                        logger.debug("response is not JSON")
                        res = response[1].decode("utf-8", "ignore")
                    return res
                elif (
                    type(response) == tuple
                    and response[0]["status"] == "403"
                    and third_party_warning in str(response[1])
                ):
                    logger.debug("Third party blocked warning")
                    return {}
                elif type(response) == tuple and response[0]["status"] != "200":
                    if ignore_errors:
                        return {}
                    else:
                        raise Exception("bad response!")
            else:
                response = requests.get(
                    url, params=params, data=data, timeout=self.timeout
                )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.info("No items found for {data}".format(**locals))
                return {}
            elif response.status_code == 400:
                if not ignore_errors:
                    raise Exception(
                        "Bad Request: you probably have incorrect parameter (values), refer to the API documentation"
                    )
                else:
                    logger.warn("400 exception!")
                    return {}
            elif response.status_code == 403:
                if not ignore_errors:
                    raise Exception(
                        "Forbidden status code (403): your API Key is wrong or your options require OAuth! (not supported here)"
                    )
                else:
                    logger.warn("403: forbidden")
                    return {"status": "forbidden"}
            elif response.status_code == 401:
                if not ignore_errors:
                    raise Exception(
                        "You misspelled a parameter, have a bad API key or require (new) OAuth (try reset_oauth?) "
                    )
                else:
                    logger.warn("401 error!")
                    return {}
            else:
                raise Exception(
                    "incorrect status code! {response.status_code} : {response.reason}".format(
                        **locals()
                    )
                )
        except (ConnectTimeout, ConnectionError):
            if retries > 0:
                return self._get(url, params, data, retries - 1, timeout)
            else:
                logger.warning(
                    "retries for {url} exceeded (params={params}, data={data})".format(
                        **locals()
                    )
                )
                return {}


class youtube_videos_search(youtube):
    """class to retrieve YouTube videos based on search queries"""

    doctype = "youtube_video"
    version = 0.1

    def get(
        self,
        credentials,
        q,
        maxpages=-1,
        expand=True,
        captions=False,
        order="date",
        **kwargs
    ):
        """Searches for videos by using queries.

        Parameters
        ---
        q        : string
            terms to search
        maxpages : int(default=-1)
            maximum pages to retrieve, -1 for infinite
        expand   : bool(default=True)
            whether to expand hits to include comment/like statistics and description
            **currently only works for videos!**
        captions : bool(default=False)
            Whether to include captions (if available)
            By default, english 'en' are retrieved, but you can override this
            by passing the 'language="nl"' keyword argument (with nl, i.e. Dutch)
            in this example.
        order : string(default='date')
            Method of ordering results, defaults to reverse chronological.
            Other options include: 'relevance','rating','title','videoCount','viewCount'

        kwargs: Please refer to https://developers.google.com/apis-explorer/#search/search/m/youtube/v3/youtube.search.list'
        for more information on possible criteria (passed as additional named arguments to the API)

        Yields
        ---
        dict per retrieved resource

        """

        self._credentials = credentials
        self.API_KEY = json.loads(self._credentials["_source"]["credentials"])[
            "access_token"
        ]

        url = "https://www.googleapis.com/youtube/v3/search"
        data = {
            "key": self.API_KEY,
            "type": "video",
            "part": "snippet",
            "maxResults": 50,
            "q": q,
            "order": order,
        }

        data.update({k: v for k, v in kwargs.items() if v})
        res = self._get(url, params=data)
        if expand and res:
            res["items"] = self.expand_videos(res["items"])
        if captions and res:
            res["items"] = self.get_captions(res["items"], **kwargs)
        for item in res.get("items", []):
            yield self._standardize_id(item)
        maxpages -= 1
        while maxpages != 0 and res.get("nextPageToken", 0):
            maxpages -= 1
            item["PAGE"] = data.get("nextPageToken", "")
            data.update({"pageToken": res["nextPageToken"]})
            logger.info("searchpage = %s" % res["nextPageToken"])
            res = self._get(url, params=data)
            if expand and res:
                res["items"] = self.expand_videos(res["items"])
            if captions and res:
                res["items"] = self.get_captions(res["items"], **kwargs)
            for item in res.get("items", []):
                yield self._standardize_id(item)

    def expand_videos(self, vids, **kwargs):
        if not vids:
            return vids
        videos = {
            vid.get("id", False): vid
            for vid in self.video_information(vids, **kwargs)
            if vid
        }
        for vid in vids:
            vid.update(videos.get(vid["id"]["videoId"], {}))
        return vids

    def video_information(self, videos, parts="all", **kwargs):
        """
        Retrieves information (not comments) about a list of videos.

        Parameters
        ---
        videos: list
            The 'items' part of a video-search or a list of videoId's

        parts: string(default='all')
            The properties to retieve per video, some may require OAuth,
            for example 'suggestions'.
        kwargs:
            keyword-arguments passed as parameters to the API, see the
            documentation for details ( https://developers.google.com/youtube/v3/docs/videos )
        """
        if not videos:
            yield

        all_parts = {
            "contentDetails": 2,
            #'fileDetails': 1,
            "id": 0,
            #'liveStreamingDetails': 2,
            #'localizations': 2,
            #'player': 0,
            #'processingDetails': 1,
            #'recordingDetails': 2,
            "snippet": 2,
            "statistics": 2,
            #'status': 2,
            #'suggestions': 1,
            "topicDetails": 2,
        }

        if parts == "all":
            parts = all_parts.keys()
        if type(parts) != str:
            parts = ",".join(parts)

        if type(videos) == list and videos and type(videos[0]) == dict:
            ids = ",".join([vid.get("id", {}).get("videoId") for vid in videos])
        elif type(videos) == list and videos and type(videos[0]) == str:
            ids = ",".join(videos)
        elif type(videos) == str:
            ids = videos
        else:
            raise Exception("Unknown videos type!")

        data = {
            "key": self.API_KEY,
            "part": parts,
            "id": ",".join([vid.get("id", {}).get("videoId") for vid in videos]),
        }
        data.update({k: v for k, v in kwargs.items() if v})
        res = self._get("https://www.googleapis.com/youtube/v3/videos", params=data)
        for vid in res.get("items", []):
            yield vid

    def get_captions(self, vids, part="id, snippet", language="en", *args, **kwargs):
        if type(vids) == str:
            vids = [{"id": vids}]
        elif type(vids) == dict:
            vids = [vids]

        url = "https://www.googleapis.com/youtube/v3/captions"

        data = {"key": self.API_KEY, "part": part}

        for vid in vids:
            if not vid["kind"] == "youtube#video":
                logger.debug("not a video, no captions retrieved")
                continue
            if vid.get("contentDetails", {}).get("caption", "true") == "true":
                if type(vid["id"]) == str:
                    data.update({"videoId": vid["id"]})
                elif type(vid["id"]) == dict:
                    data.update({"videoId": vid["id"]["videoId"]})
                captions = self._get(url, params=data).get("items", [])
            else:
                continue  # if captions are known not to exist, skip them
            vid["captions"] = captions
            cap = self.get_caption(vid, language=language, **kwargs)
            if type(cap) == dict and not cap:
                cap = ""
            vid["caption"] = cap

        return vids

    def get_caption(self, vid, language, types=["standard", "ASR"], *args, **kwargs):
        caption_url = "https://www.googleapis.com/youtube/v3/captions/"
        data = {"tfmt": "srt"}
        if vid.get("captions"):
            has_caps = {
                num: [
                    cap
                    for cap in vid["captions"]
                    if cap.get("snippet", {}).get("language", "") == language
                    and cap.get("snippet", {}).get("trackKind", "") == captype
                ]
                for num, captype in enumerate(types)
            }
            # remove empty levels
            has_caps = {k: v for k, v in has_caps.items() if v}
            if not has_caps:
                return {"none": ""}
            best_choice = min(list(has_caps.keys()) + [10])
            if best_choice < 10:
                cap = self._get(
                    caption_url + has_caps[best_choice][0]["id"],
                    params=data,
                    oauth=True,
                )
                if type(cap) == dict and not cap:
                    cap = ""
                return {types[best_choice]: cap}

        else:
            return {"none": ""}


class youtube_comments(youtube):

    doctype = "youtube_comments"
    version = 0.1

    def get(
        self,
        credentials,
        parent_id,
        for_type="video",
        maxpages=-1,
        include_replies=True,
    ):
        """Retrieve youtube_comments for specified ids

        Parameters
        ----------
        parent_id : string or dict
            A YouTube id for which to retrieve comments, or a video.
        for_type : string(default=video)
            The type of resource for which to retrieve comments, can be either
            "video" for videos (default), "channel" for YouTube channels or
            "channel+videos" which includes all comment threads related to a
            channel
        maxpages : int(default=-1)
            An integer to specify the number of 100-result pages to retrieve.
            -1 marks all available comments (default).
        include_replies : bool(default=True)
            Whether to include replies in addition to top level comments

        Yields
        ------
        dict for each toplevelcomment or reply
        """

        self._credentials = credentials
        self.API_KEY = json.loads(self._credentials["_source"]["credentials"])[
            "access_token"
        ]

        parts = "snippet"

        url = (
            "https://www.googleapis.com/youtube/v3/commentThreads"
        )  # appropriate comments endpoint

        # Allow for 'video' object to be either dicts or strings
        if type(parent_id) == dict:
            rid = parent_id.get("_source", {}).get("id")
        elif type(parent_id) == str:
            rid = parent_id
        else:
            raise Exception(
                "unknown video argument type, should be a dict with an id key, or a sring!"
            )

        # the data will be used as the parameters of the request
        data = {
            "key": self.API_KEY,  # For authentication purposes
            "part": parts,
            "maxResults": 100,  # Assume we want the maximum results possible
        }

        # pass the right parameter for videos, channels or channels+videos (allThreadsRelatedToChannel)
        if for_type == "video":
            data.update({"videoId": rid})
        elif for_type == "channel":
            data.update({"channelId": rid})
        elif for_type == "channel+videos":
            data.update({"allThreadsRelatedToChannelId": rid})
        else:
            raise Exception(
                "for_type should be 'video', 'channel' or 'channel+videos'!"
            )

        res = self._get(url, params=data)
        for item in res.get("items", []):
            repliespresent = item["snippet"]["totalReplyCount"]
            parent_id = item["id"]
            item["commenttype"] = "toplevelcomment"
            yield item
            if repliespresent == 0:
                pass
            elif repliespresent > 0 and include_replies:
                for reply in self._get_replies(parent_id):
                    reply["commenttype"] = "reply"
                    yield reply

        while maxpages != 0 and res.get("nextPageToken", False):
            maxpages -= 1
            data.update({"pageToken": res.get("nextPageToken", False) or None})
            res = self._get(url, params=data)
            for item in res.get("items", []):
                repliespresent = item["snippet"]["totalReplyCount"]
                parent_id = item["id"]
                item["commenttype"] = "toplevelcomment"
                yield item

                if repliespresent == 0:
                    continue
                elif repliespresent > 0 and include_replies:
                    for reply in self._get_replies(parent_id):
                        reply["commenttype"] = "reply"
                        yield reply

    def _get_replies(self, parent_id, maxpages=-1):
        """Internal method to retrieve replies to topLevelComments
        Please call by supplying the include_replies=True parameter to the
        youtube_comments function.

        """
        parts = "snippet"

        url = (
            "https://www.googleapis.com/youtube/v3/comments"
        )  # appropriate comments endpoint

        # the data will be used as the parameters of the request
        data = {
            "key": self.API_KEY,  # For authentication purposes
            "part": parts,
            "maxResults": 100,  # Assume we want the maximum results possible
            "parentId": parent_id,
        }

        logger.debug("Retrieving YouTube reply for {parent_id}".format(**locals()))
        res = self._get(url, params=data)
        for item in res.get("items", []):
            yield item
        while maxpages != 0 and res.get("nextPageToken", False):
            maxpages -= 1
            data.update({"pageToken": res.get("nextPageToken", False) or None})
            res = self._get(url, params=data)
            for item in res.get("items", []):
                yield item
