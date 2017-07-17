'''
This file provides the base-class for API clients
'''
from core.scraper_class import Scraper
from clients._general_utils import *
from core.database import config
import time
import datetime
import logging

logger = logging.getLogger("INCA"+__name__)

APPLICATIONS_INDEX = "_apps"
CREDENTIALS_INDEX  = "_credentials"



class Client(Scraper):
    '''Clients provide access to APIs.

    Subclasses of `Client` should implement the following:

    `service_name` should be a string that declares the service for which credentials are used

    add_credential: method
        Take the required steps to get new credential, returns (id, credentials) tuple consumable by the 'get' method

    credential_usage_condition: string, (default=None)
        condition to use a credential

    get: method
        should expect a 'credentials' argument that reflects the credentials stored by add_credentials
        Get new content, probably defined in the subclass of a service subclass. i.e.:

        class twitter(Client):

            service = "twitter"

            def add_app(appname='defaut'):
                app_credentials = self.prompt({...})
                self.create_app(name=appname, app_credentials)



            def add_credentials():
                ...
                if load_credentials(id=username):
                    add_credentials()
                else:
                    # 1. prompt user
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

    def get(self, credentials, *args, **kwargs):
        """OVERRIDE THIS METHOD

        This method should implement the retrieval functionality for
        a given API service. It should expect a dictionary of
        credentials.

        yields
        ------
        none
            none, but should yield documents when implemented
        """
        logger.warning("THIS METHOD IS NOT IMPLEMENTED")
        yield

    def add_app(self,appname="default", token=None, secret=None):
        """OVERRIDE THIS METHOD

        This method should implement the app certification process,
        taking some user inputs and passing the resulting app
        token ad secret to the `self.store_application` method.

        token and secret arguments should be respected for scenarios
        in which no user-interaction is enabled.


        """
        logger.warning("THIS METHOD IS NOT IMPLEMENTED")
        return False

    def add_credentials(self, appname="default"):
        """OVERRIDE THIS METHOD

        This method should implement the user interaction loop
        required to get consumer keys and consumer tokens for
        a given app, i.e. the user credentials.

        Retrieve the appropriate app credentials with
        `self.load_application`, create a credentials dictionary
        and store them by calling the `self.store_credentials` method.

        Returns
        -------
        boolean
            indication of app generation success
        """
        logger.warning("THIS METHOD IS NOT IMPLEMENTED")
        return False

    def run(self,app='default', *args, **kwargs):
        """Run the .get() method of a class

        This is the wrapper that calls the `self.get()` method implemented
        in child classes. It provides these classes with a credentials={...}
        argument based on the credentials returned by `self.load_credentials`.
        See the docstring of that function for explanations about indicating
        selection criteria for classes.

        """
        credentials = load_credentials(app=app)
        if credentials:
            usable_credentials = credentials['_source'].get('credentials',{})
        else:
            usable_credentials = {}
        return super(Client, self).run(credentials=usable_credentials, *args, **kwargs)


    def store_application(self, app_credentials, appname="default"):
        """Create a new app to which credentials can be tied

        Oauth services require an app as a basis for credentials. In INCA
        apps function both to provided the authentication tokens to create
        new credentials, but also as a way to 'bundle' these credentials. If
        no appname is specified, they are tied to the 'default' app (internal
        name). This is generally fine when data-collection does not care
        about which of the credentials for this service is used. In other words:
        when all data collection uses the set of credentials, the appname can
        be left as 'default' in all calls.

        Parameters
        ----------
        app_credentials : dictionary
            The appliction-level credentials required to create user credentials
            stored under 'source.credentials' in the ES document
        appname : string (default='default')
            The internal designation for the app, used to seperate credentials
            provided for different purposes/projects

        Returns
        -------
        dictionary
            the ES document created or an empty dictionary on failure

        Notes
        -----
        `appname` is an internal indicator only. The name given to the app in
        the service (e.g. Twitter, Youtube, etcetera) is immaterial to this name.


        """

        return {}

    def load_application(self, app="default"):
        """Loads a specified application

        This function returns the named application, based in part on
        `self.service_name`. This function is oriented mainly to support the
        credentials generation process (where the app credentials are required
        to create consumer-credentials). You probably want to store all required
        keys in the credentials and not call this function for anything but
        registering new user credentials.

        Parameters
        ----------
        app : string (default='default')
            The internal application name specified in the store_application
            call to identify the appropriate credentials.

        Returns
        -------
        dictionary
            The application credentials or empty if no application is found

        """
        return {}

    def remove_application(self, app):
        """Removes an application

        Removes an application, thus preventing new credentials from being
        generated. All credentials with this app name are also removed for
        this service (e.g. {service}_{pool})

        Parameters
        ----------
        app : string
            The application to remove

        Returns
        -------
        boolean
            Indicator of success

        """
        pass


    def store_credentials(self, id, app='default', credentials={}, content={}):
        """adds a new credential to a app in the database

        Credentials are the authentication keys for API clients. They are divided
        in "apps", so that one instance of INCA can seperate credentials supplied
        for different ends. Credentials are automatically provided to client.get()
        methods when client.run() is called.

        Generating credentials usually entails some (end-)user action, such as
        clicking on a link, going to a website and writing down some code. Such
        functionality is client-specific, and should be in the ServiceName(Client)
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
        app : string (default=default)
            A string that identiefies the app of credentials to which this
            credential should be added. this will be stored in the _credentials
            index with the doctype <service_name>_<app>
        credentials : dictionary
            A dictionary that should be provided for client.get methods as the
            `credentials` parameter. Generally contains the application token and
            secret, as well as the consumer token and secret
        content : dictionary (default={})
            Additional information that may be provided for other purposes.
            Empty by default.

        Returns
        -------
        boolean
            A True or False value indicating succesful saving.


        """

        return False

    def load_credentials(self, app='default', id=None):
        """Load a credential from the specified app

        Retrieves credentials from a specified app. Choices are based
        on the `sort_field` and `preference` class properties that should
        indicate which field indicates how suited a credential is. If the
        class properties `sort_field` and `preference` are not set, it defaults
        to `last_loaded.<self.__name__>` & `lowest`, i.e. the credential that
        has not been used this function the longest time.

        Parameters
        ----------
        app : string (default='default')
            the appname from which the credentials should be drawn. Will be
            prepended with service name, i.e. "{service_name}_{appname}"

        id   : string (default=None)
            a specific credential ID to retrieve, for instance related to
            user-specific content (e.g. direct messages). Otherwise the
            `self.sort_field` and `self.preference` are used to select
            credentials to apss to the .get method. NOTE: overrides app

        Returns
        -------
        dictionary
            the credentials record (empty if not found)

        Notes
        -----
        This function updates the last_loaded.<classname> field with the current
        time.

        """
        pass

    def update_credentials(self, id, content, app='default'):
        """Update credentials information

        This method should be called to add additional information to
        credentials, such as a rate-limit-remaining status that can be used to
        designate which credentials are prefered. The results are added to the
        storage field of the credentials.

        Parameters
        ----------
        id : string
            ES ID of the credentials to update. Probably specified in the call
            to `store_credentials`
        content : dictionary
            The content to add, or update, for this record
        app : string (default='default')
            The appname in which the credential is stored.

        Example
        -------
        client.store_credentials(id='test1',credentials={
            "apptoken":"nope",
            "appsecret":"nope",
            "consumerkey":"nope",
            "consumersecret":"nope"
            })
        client.update_credentials(id='test1',app='default',content={'comment':
            "no coment"})
        client.load_credentials(id='test1',app='default')
        >>> {
            "_id" : "test1",
            "_index" : "_credentials".
            "_doctype": "service_class",
            "source": {
                "credentials": {
                    "apptoken":"nope",
                    "appsecret":"nope",
                    "consumerkey":"nope",
                    "consumersecret":"nope"
                    },
                "content" : {
                    "comment" : "no comment"
                    }

            }

        }

        """
        pass

        def postpone(
            seconds=0,
            minutes=0,
            hours=0,
            days=0,
            until=None,
            *args,
            **kwargs
             ):
            """postpones call to self.run()

            Given a delay time or start time, postpones call to the run method.
            This is usefull when credentials have all been expended.

            Parameters
            ----------
            seconds : int (default=0)
                The number of seconds to delay
            minutes : int (default=0)
                The number of minutes to delay
            hours : int (default=0)
                The number of hours to delay
            days : int (default=0)
                The number of days to delay
            until : datetime object
                Time at which the task should be resumed
            *args, **kwargs
                Arguments passed to the `.run()` method

            Returns
            -------
            None

            Notes
            -----
            The 'until' time overrides all other non-args/kwargs arguments

            """
            if until
