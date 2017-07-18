'''
This file contains the twitter API retrieval classes
'''

from core.client_class import Client, elasticsearch_required
from core.basic_utils import dotkeys
from twython import Twython, TwythonRateLimitError
from core.database import client as database_client
import logging
import sys
import time

logger = logging.getLogger("INCA.%s" %__name__)

class twitter(Client):
    '''Class defined mainly to add credentials'''

    service_name = "twitter"

    @elasticsearch_required
    def add_application(self, appname="default"):
        """Add a Twitter app to generate credentials """

        app_prompt = {
            'header' : "Add Twitter application",
            'description':
                "Please go to https://apps.twitter.com and click on 'Create New App' \n"
                "Enter any name you'd like for this app, but realize that every \n"
                "user who is asked to contribute credentials will see this name. \n"
                "\n"
                "Add a website, this can be a placeholder if your are not worried \n"
                "about users trying to read up on your project, such as 'http://placeholder.com'\n"
                "\n"
                "Agree to the developpers agreement\n"
                "Press 'Create your Twitter application'\n"
                "\n"
                "Under Application Settings, click on 'manage keys and access tokens'\n",

            'inputs' : [
                {
                    'label': 'Application name',
                    'description': "Name for internal use",
                    'help' : "Just a string to denote the application within INCA",
                    'input_type':'text',
                    'mimimum' : 4,
                    'maximum' : 15,
                    'default' : appname,
                },
                {
                    'label': 'Application Consumer Key',
                    'description': "Copy-paste the code shown in the 'Consumer Key (API Key)' field",
                    'help' : "Make sure you are at the 'Key access and tokens' tab of your application settings",
                    'input_type':'text',
                    'mimimum' : 8,
                },
                {
                    'label': 'Application Consumer Secret',
                    'description': "Copy-paste the code shown in the 'Consumer Secret (API Secret)' field",
                    'help' : "Make sure you are at the 'Key access and tokens' tab of your application settings",
                    'input_type':'text',
                    'mimimum' : 8,
                }

                ]

        }
        response = self.prompt(app_prompt, verify=True)
        return self.store_application(
            app_credentials={
                'consumer_key'    : response['Application Consumer Key'],
                'consumer_secret' : response['Application Consumer Secret']
        }, appname=response['Application name'])

    @elasticsearch_required
    def add_credentials(self, appname='default'):
        '''Add credentials to a specified app '''

        logger.info("Adding credentials to {appname}".format(**locals()))

        application = self.load_application(app=appname)
        if not application:
            logger.warning("Sorry, no application found")
            return False
        consumer_key    = dotkeys(application, '_source.credentials.consumer_key')
        consumer_secret = dotkeys(application, '_source.credentials.consumer_secret')

        twitter = Twython(consumer_key, consumer_secret)
        auth    = twitter.get_authentication_tokens()

        user_prompt = {
            'header' : "authenticate for {appname}".format(appname=appname),
            'description' : "Please visit {auth[auth_url]} in your browser and \n"
            "accept the invitation to this application. \n"
            "Copy the code shown on this page and enter it below.".format(**locals()),
            "inputs" : [
                {
                'label' : "authentication code",
                'description': "code provided on link",
                'help'  : "make sure you accept access and copy the 4 digits",
                'input_type' : "text",
                "minimum" : 4,
                "maximum" : 12
                }

            ]
        }
        response = self.prompt(user_prompt, verify=True)
        code    = response['authentication code']
        twitter = Twython(consumer_key, consumer_secret, auth['oauth_token'],auth['oauth_token_secret'])
        credentials = twitter.get_authorized_tokens(code)
        credentials.update({'consumer_key':consumer_key, 'consumer_secret':consumer_secret})

        logger.info("Checking rate limit status")
        api = self._get_client(credentials)
        status = api.get_application_rate_limit_status()

        return self.store_credentials(app=appname, credentials=credentials, id=credentials['user_id'], **status)


    def _get_client(self, credentials):
        return Twython(
            credentials['consumer_key'],
            credentials['consumer_secret'],
            credentials['oauth_token'],
            credentials['oauth_token_secret']
        )

    def _set_delay(self, *args, **kwargs):
        now = time.time()
        earliest = self.load_credentials(app=app,update_last_loaded=False)
        if earliest:
            resettime = dotkeys(earliest,self.sort_field)
            delay_required = resettime - now
            if delay_required < 0 :
                self.run(*args, **kwargs)
            self.postpone(delaytime = delay_required, *args, **kwargs )
        else:
            info.warn("No credentials available...")

class twitter_timeline(twitter):
    '''Class to retrieve twitter timelines for a given account'''

    sort_field = "content.resources.statuses./statuses/user_timeline.reset"
    preference = 'lowest'

    def get(self, credentials, screen_name, force=False, max_id=None, since_id=None):
        '''retrieved from the twitter user_timeline API'''

        self.doctype =  "tweets"
        self.version = "0.2"
        self.functiontype = "twitter_client"

        api = self._get_client(credentials=dotkeys(credentials, '_source.credentials'))
        try: self.update_credentials(credentials['_id'], **api.get_application_rate_limit_status())
        except TwythonRateLimitError: pass # sometimes you just can't get a rate-limit estimate

        if not force:
            since_id = self._first_added().get('_source',{}).get("id",None)
            logger.info("settings since_id to {since_id}".format(**locals()))
        try:
            batchsize = 1
            while batchsize:

                tweets = api.get_user_timeline(screen_name=screen_name,
                                               max_id=max_id,
                                               since_id=since_id,
                                               count=200)
                batchsize = len(tweets)

                if not batchsize: continue
                max_id = min([ tweet.get('id',None) for tweet in tweets ])-1
                for num, tweet in enumerate(tweets):
                    if self._check_exists(tweet['id_str'])[0] and not force:
                        logger.info(
                             "skipping existing {screen_name}-{tweet[id]}".format(**locals())
                            )
                        continue
                    tweet['_id'] = tweet['id_str']
                    if not (num+1) % 100:
                        logger.info("retrieved {num} tweets for {screen_name}, at {tweet[_id]}".format(**locals()))

                    yield tweet

            self.update_credentials(credentials['_id'], **api.get_application_rate_limit_status())
        except TwythonRateLimitError:
            logger.info('expended credentials')
            try: self.update_credentials(credentials['_id'], **api.get_application_rate_limit_status())
            except TwythonRateLimitError: # when a ratelimit estimate is unavailable
                self.postpone(self, delaytime=60*5, screen_name=screen_name,
                              force=force, max_id=max_id, since_id=since_id)
            max_id = self._last_added().get("_source",{}).get("id",None)
            self._set_delay(
                            timeout_key="last.resources.statuses./statuses/user_timeline.reset",
                            screen_name=screen_name,
                            force=force,
                            max_id=max_id,
                            since_id=since_id
                            )
