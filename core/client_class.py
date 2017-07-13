'''
This file provides the base-class for API clients
'''
from core.scraper_class import Scraper
from clients._general_utils import *
from core.database import config
import time

class Client(Scraper):
    '''Clients provide access to APIs. Clients sublcasses should provide the following functionality

    service_name should be a string that declares the service for which credentials are used

    Subclasses of `Client` should implement the following:

    add_credential: method
        Take the required steps to get new credential, returns (id, credentials) tuple consumable by the 'get' method

    credential_usage_condition: string, (default=None)
        condition to use a credential

    get: method
        should expect a 'credentials' argument that reflects the credentials stored by add_credentials
        Get new content, probably defined in the subclass of a service subclass. i.e.:

        class twitter(Client):

            service = "twitter"

            def add_twitter_app(appname='defaut'):
                app_credentials = self.prompt({...})
                self.create_app(name=appname, app_credentials)



            def add_credentials():
                ...
                return True


        class get_timeline(twitter):

            sort_field = "rate_limit_remaining.resettime"
            preference = "lowest"

            def get(self, credentials, username, ....):
                # do stuff
                for n,i in enumerate(api_call()):
                    if n>0 and api_limit_reached:
                        for doc in self.get(**locals()):
                        yield doc
                    elif n==0 and api_limit_reached:
                        postone(minutes=5)

                yield doc



    '''

    service_name = "UNKNOWN"

    sort_field = ""

    preference = ""

    def run(self,pool='default', *args, **kwargs):
        '''Get stuff from the client through Scraper.run() method, by adding credential keyword'''
        credentials = get_credentials(self.service_name,
                                      pool_name=pool,
                                      filter=self.credential_usage_condition())
        if credentials:
            usable_credentials = (credentials['_id'],credentials['_source'].get('credentials',{}))
        else:
            usable_credentials = ()
        return super(Client, self).run(credentials=usable_credentials, *args, **kwargs)


    def store_credentials(self, id, pool='default', credentials):
        """adds a new credential to a pool in the database

        Credentials are the authentication keys for API clients. They are divided
        in "pools", so that one instance of INCA can seperate credentials supplied
        for different ends. Credentials are automatically provided to client.get()
        methods when client.run() is called.

        Generating credentials usually entails some (end-)user action, such as
        clicking on a link, going to a website and writing down some code. Such
        fuctionality is client-specific, and should be in the ServiceName(Client)
        Class. This function assumes you have retrieved (and verified) the response
        and now poses a dictionary that contains all the information you need to
        autheticate to the API, i.e. the application token & secret and the
        consumer token and secret. By passing this dictionary tot this function,
        they are stored in ES and will be provided as the credentials argument
        to the get method of your function.

        Parameters
        ----------
        id   : string
            The identifier of this credentials set, generally the user_id for
            the service. Used to list the available credentials
        pool : string (default=default)
            A string that identiefies the pool of credentials to which this
            credential should be added. this will be stored in the _credentials
            index with the doctype <service_name>_<pool>
        credentials : dictionary
            A dictionary that should be provided for client.get methods as the
            `credentials` parameter. Generally contains the application token and
            secret, as well as the consumer token and secret

        Returns
        -------
        boolean
            A True or False value indicating succesful saving.
        """

        return False

    def load_credentials(self, pool, id=None):
        """Load a credential from the specified pool

        Retrieves credentials from a specified pool. Choices are based
        on the `sort_field` and `preference` class properties that should
        indicate which field indicates how suited a credential is. If the
        class properties `sort_field` and `preference` are not set, it defaults
        to `last_loaded.<self.__name__>` & `lowest`, i.e. the credential that
        has not been used this function the longest time.

        Parameters
        ----------
        pool : string
            the poolname from which the credentials should be drawn. Will be
            prepended with service name, i.e. "{service_name}_{poolname}"

        id   : string (default=None)
            a specific credential ID to retrieve, for instance related to
            user-specific content (e.g. direct messages). Otherwise the
            `self.sort_field` and `self.preference` are used to select
            credentials to apss to the .get method.

        Returns
        -------
        dictionary
            a dictionary of credentials, as provided to the store_credentials
            function

        Notes
        -----
        This function updates the last_loaded.<classname> field with the current
        time.

        """

    def update_credentials(self, pool, id, content):
        """Update credentials information

        This method should be called to add additional information to
        credentials, such as a rate-limit-remaining status that can be
        retrieved using

        """
