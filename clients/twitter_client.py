'''
This file contains the twitter API retrieval classes
'''

from core.client_class import Client
from core.basic_utils import dotkeys
from twython import Twython, TwythonRateLimitError
from core.database import config
from core.database import client as database_client
import logging
import sys
import time

logger = logging.getLogger(__name__)

class twitter(Client):
    '''Class defined mainly to add credentials'''

    service_name = "twitter"

    def add_credentials(self, CLI=True):
        '''Starts OAuth dance access tokens
        CLI: bool
            Whether to use commandline interface to authenticate (rather than WUI)
        '''
        consumer_key    = config.get('twitter','Consumer_key')
        consumer_secret = config.get('twitter','Consumer_secret')

        if consumer_key == "get_at_twitter" or consumer_secret =="get_at_twitter":
            logger.info('No consumer key or secret available, please download these and add them to settigns.cfg')
            return False

        if CLI:
            twitter = Twython(consumer_key, consumer_secret)
            auth    = twitter.get_authentication_tokens()
            code    = _interact("Please enter the code found through: {auth[auth_url]} :".format(**locals())).strip()
            twitter = Twython(consumer_key, consumer_secret, auth['oauth_token'],auth['oauth_token_secret'])
            credentials = twitter.get_authorized_tokens(code)
            return (credentials['user_id'], credentials)

        else: # TODO: add non-CLI interface!!
            logger.warning("No non-CLI interface available")

    def _get_client(self, credentials):
        return Twython(
            config.get('twitter', 'Consumer_key'),
            config.get('twitter', 'Consumer_secret'),
            credentials[1]['oauth_token'],
            credentials[1]['oauth_token_secret']
        )

    def _set_delay(self, timeout_key, *args, **kwargs):
        now = time.time()
        earlies = database_client.search(
            index='credentials',
            doc_type="twitter",
            body= {
                "sort": {
                    timeout_key:{"order":"asc"}
                        }
                    }
        )['hits']['hits']
        if earlies:
            resettime = dotkeys(earlies[0]['_source'],timeout_key)
            delay_required = resettime - now
            if delay_required < 0 :
                self.run(*args, **kwargs)
            self.postpone(delaytime = delay_required, *args, **kwargs )
        else:
            info.warn("No credentials available...")

def _interact(message):
    if sys.version_info.major == 2:
        user_input = raw_input # ensure python2 compatibility
    elif sys.version_info.major == 3:
        user_input = input
    try:
        output = user_input(message)
        if not output:
            return _interact(message)
        return output
    except KeyboardInterrupt:
        print("Stopping attempt")
        return "failed"

class twitter_timeline(twitter):
    '''Class to retrieve twitter timelines for a given account'''

    def credential_usage_condition(self):

        return  {"or": [
        {"range": {"last.resources.statuses./statuses/user_timeline.remaining": {"gte": 0}}},
        {"range": {"last.resources.statuses./statuses/user_timeline.reset": {"lte": time.time()}}},
        {"missing": {"field": "last"}}
        ]}

    def get(self, credentials, screen_name, force=False, max_id=None, since_id=None):
        '''retrieved from the twitter user_timeline API'''

        self.doctype =  "tweets"
        self.version = "0.1"
        self.functiontype = "twitter_client"

        if not credentials:
            self._set_delay(
                            timeout_key="last.resources.statuses./statuses/user_timeline.reset",
                            screen_name=screen_name,
                            force=force,
                            max_id=max_id,
                            since_id = since_id
            )

        api = self._get_client(credentials=credentials)
        self.update_last(credentials[0], api.get_application_rate_limit_status())
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

            self.update_last(credentials[0], api.get_application_rate_limit_status())
        except TwythonRateLimitError:
            logger.info('expended credentials')
            self.update_last(credentials[0], api.get_application_rate_limit_status())
            max_id = self._last_added().get("_source",{}).get("id",None)
            self._set_delay(
                            timeout_key="last.resources.statuses./statuses/user_timeline.reset",
                            screen_name=screen_name,
                            force=force,
                            max_id=max_id,
                            since_id=since_id
                            )