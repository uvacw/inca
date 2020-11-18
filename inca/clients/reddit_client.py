from ..core.client_class import Client, elasticsearch_required
from ..core.basic_utils import dotkeys
import praw
import json
import hashlib
import logging
logger = logging.getLogger("INCA.%s" % __name__)

class reddit(Client):
    """
    Class defined mainly to add credentials
    """

    service_name = "reddit"

    @elasticsearch_required
    def add_application(self, appname="default"):
        """
        Add a Reddit app
        """

        app_prompt = {
            "header": "Add Reddit application",
            "description": "Please go to https://www.reddit.com/prefs/apps and click on 'create app'.\n"
                           "Fill out the form that appears:\n"
                           "name: enter any name you'd like for the app\n"
                           "type of app: select 'script'\n"
                           "description: (optional field)\n"
                           "about url: (optional field)\n"
                           "redirect uri: 'http://localhost:8080'\n"
                           "(a script app doesn't involve redirection, but Reddit requires this field to be filled to create the app)\n"
                           "Go to https://www.reddit.com/wiki/api and follow the API requirements (e.g. registering the app).\n",
            "inputs": [
                {
                    "label": "Application Name",
                    "description": "Name for internal use",
                    "help": "Just a string to denote the application within INCA",
                    "input_type": "text",
                    "mimimum": 4,
                    "maximum": 15,
                    "default": appname,
                },
                {
                    "label": "Application Client Id",
                    "description": "Copy-paste the code shown on your app",
                    "help": "You can find the client ID under your app's listing at https://www.reddit.com/prefs/apps",
                    "input_type": "text",
                    "mimimum": 8,
                },
                {
                    "label": "Application Client Secret",
                    "description": "Click 'edit' and copy-paste the code shown in the 'secret' field",
                    "help": "You can find the client secret under your app's listing at https://www.reddit.com/prefs/apps",
                    "input_type": "text",
                    "mimimum": 8,
                },
                {
                    "label": "Application User-Agent String",
                    "description": "use the following format:\n"
                                   "'script:app_ID:app_version (by /u/username)'\n"
                                   "for example: 'script:my_reddit_app:v1 (by /u/my_reddit_username)'\n",
                    "help": "Reddit requires that the User-Agent string is unique and descriptive of your app:\n" 
                            "Please see https://github.com/reddit-archive/reddit/wiki/API for more details.\n",
                    "input_type": "text",
                    "mimimum": 8,
                }
            ],
        }
        response = self.prompt(app_prompt, verify=True)
        return self.store_application(
            app_credentials={
                "client_id": response["Application Client Id"],
                "client_secret": response["Application Client Secret"],
                "client_useragent": response["Application User-Agent String"]
            },
            appname=response["Application Name"]
        )

    @elasticsearch_required
    def add_credentials(self, appname="default"):
        """
        Add credentials to a specified app
        """

        logger.info("Adding credentials to {appname}".format(**locals()))

        application = self.load_application(app=appname)
        if not application:
            logger.warning("Sorry, no application found")
            return False

        user_prompt = {
            "header": "Provide your Reddit username",
            "description": "INCA uses your Reddit username for storing credentials internally.\n",
            "inputs": [
                {
                    "label": "Account Username",
                    "description": "Type in the username of the account you used to create the app on Reddit.\n",
                    "help": "",
                    "input_type": "text",
                    "mimimum": 3,
                }
            ],
        }

        response = self.prompt(user_prompt, verify=True)

        credentials = {"client_id": dotkeys(application, "_source.credentials.client_id"),
                       "client_secret": dotkeys(application, "_source.credentials.client_secret"),
                       "user_agent": dotkeys(application, "_source.credentials.client_useragent")
                       }

        return self.store_credentials(
            app=appname,
            credentials=json.dumps(credentials),
            id=response["Account Username"]
        )

    def _get_client(self, credentials):
        """
        Get a read-only instance of PRAW's (Python Reddit API Wrapper) Reddit class.
        """

        if type(credentials) == str:
            credentials = json.loads(credentials)
        return praw.Reddit(
            client_id = credentials["client_id"],
            client_secret = credentials["client_secret"],
            user_agent = credentials["user_agent"]
        )


class reddit_posts(reddit):
    """
    "posts" is a generic term used to refer to PRAW's Submission and Comment classes

    - id prefixes:
        comment_kind=t1
        redditor_kind=t2
        submission_kind=t3
        message_kind=t4
        subreddit_kind=t5
        trophy_kind=t6
    """

    doctype = "reddit_post"
    version = 0.1

    def get(self,
            credentials,
            subreddit_name,
            pseudo_output=True,
            max_results=5 # Reddit's API returns up to 1,000 results if 'limit=None'
    ):

        api = self._get_client(credentials=dotkeys(credentials, "_source.credentials"))

        # get a subreddit
        subreddit = api.subreddit(subreddit_name)

        for submission in subreddit.new(limit=max_results):
            submission.title  # makes submission non-lazy to get more attributes
            submission.comments.replace_more(limit=None)  # expand the submission's CommentForest
            yield from self._get_submission(submission=submission, pseudo_output=pseudo_output)

            if len(submission.comments) > 0:
                for comment in submission.comments:
                    yield from self._process_comment(comment=comment, pseudo_output=pseudo_output, depth=1)

    def _get_submission(self, submission, pseudo_output):
        """
        Yields a dictionary of content related to a PRAW Submission.
        The depth is set to 0 to indicate that this post is at the top-level within a thread.
        """

        try:
            submission_content = dict(
                subreddit_name_prefixed=submission.subreddit_name_prefixed if hasattr(submission,'subreddit_name_prefixed') else None,
                subreddit_id=submission.subreddit_id if hasattr(submission, 'subreddit_id') else None,
                created_utc=submission.created_utc if hasattr(submission, 'created_utc') else None,
                id='t3_' + submission.id if hasattr(submission, 'id') else None,
                link_id='t3_' + submission.id if hasattr(submission, 'id') else None,
                title=submission.title if hasattr(submission, 'title') else None,
                num_comments=submission.num_comments if hasattr(submission, 'num_comments') else None,
                author_fullname=submission.author_fullname if hasattr(submission, 'author_fullname') else None,
                author_name=submission.author.name if hasattr(submission, 'author') and hasattr(submission.author, 'name') else None,
                text=submission.selftext if hasattr(submission, 'selftext') else None,
                depth=0
            )

            # raise ValueError('dummy Submission error')

            if pseudo_output:
                submission_content = self._pseudonymize(submission_content)

            yield submission_content

        except Exception as e:
            logger.warning("An exception occurred while scraping a Submission. Printing the error message:\n"
                           f"{e}\n"
                           "Attempting to print the Submission's id...\n")
            try:
                # raise ValueError('dummy Submission error in logging')
                logger.warning(f"t3_{submission.id}")

            except:
                logger.warning("failed, Submission id is unavailable.")



    def _process_comment(self, comment, pseudo_output, depth=1):
        """
        Yields a dictionary of content related to a PRAW Comment.
        A reply is also a PRAW Comment object.
        The depth is set to 1 or higher, indicating how nested a Comment is within a thread.
        Note that we don't use the 'depth' attribute of PRAW Comment (which starts at 0)
        because we want to record the top-level post's (i.e. Submission) depth as 0.
        0 = Submission
        1 = Comment on Submission (0)
        2 = Reply to Comment (1)
        3 = Reply to 1st Reply (2)
        4 = Reply to 2nd Reply (3), etc.
        - modified from https://stackoverflow.com/questions/57243140/how-to-store-a-comments-depth-in-praw
        """

        try:
            comment_content = dict(
                subreddit_name_prefixed=comment.subreddit_name_prefixed if hasattr(comment,'subreddit_name_prefixed') else None,
                subreddit_id=comment.subreddit_id if hasattr(comment, 'subreddit_id') else None,
                created_utc=comment.created_utc if hasattr(comment, 'created_utc') else None,
                id='t1_' + comment.id if hasattr(comment, 'id') else None,
                link_id=comment.link_id if hasattr(comment, 'link_id') else None,
                parent_id=comment.parent_id if hasattr(comment, 'parent_id') else None,
                author_fullname=comment.author_fullname if hasattr(comment, 'author_fullname') else None,
                author_name=comment.author.name if hasattr(comment, 'author') and hasattr(comment.author, 'name') else None,
                text=comment.body if hasattr(comment, 'body') else None,
                depth=depth
            )

            # raise ValueError('dummy Comment error')

            if pseudo_output:
                comment_content = self._pseudonymize(comment_content)

            yield comment_content

            for reply in comment.replies:
                yield from self._process_comment(comment=reply, pseudo_output=pseudo_output, depth = depth + 1)

        except Exception as e:
            logger.warning("An exception occurred while scraping a Comment. Printing the error message:\n"
                           f"{e}\n"
                           "Attempting to print the Comment's id...\n")
            try:
                # raise ValueError('dummy Comment error in logging')
                logger.warning(f"t1_{comment.id}")

            except:
                logger.warning("failed, Comment id is unavailable.")


    def _pseudonymize(self, content_dict):
        """
        :param content_dict: dictionary of content related to a Submission or Comment
        :return: dictionary with specified key values hashed for privacy
        """
        keys_to_hash = ['id',
                        'link_id',
                        'parent_id',
                        'author_fullname',
                        'author_name'
                        ]

        for key in content_dict:
            if key in keys_to_hash:
                try:
                    content_dict[key] = hashlib.sha256(content_dict[key].encode('utf-8')).hexdigest()
                except Exception as e:
                    logger.warning(f"Didn't pseudonymize '{key}' for id={content_dict['id']} because {e}. Returned value as-is.")

        return(content_dict)