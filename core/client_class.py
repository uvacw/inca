'''
This file provides the base-class for API clients

Because clients require stored credentials, the client
requires a functioning elasticsearch instance.


'''
from core.scraper_class import Scraper
from clients._general_utils import *
from core.database import DATABASE_AVAILABLE
if DATABASE_AVAILABLE:
    from core.database import client
    from elasticsearch.exceptions import ConnectionError, ConnectionTimeout, NotFoundError, RequestError
import time
import datetime
import logging

logger = logging.getLogger("INCA.%s" %__name__)

APPLICATIONS_INDEX = ".apps"
CREDENTIALS_INDEX  = ".credentials"

# It's dangerous to go alone, take this.
#
# Most functionality here will not work without ES
# use this wrapper to catch attempts to create credentials
# without an ES storage available
#
def elasticsearch_required(function):
    """Throw warning and refrain from running function when no Elasticsearch
    database is available.
    """
    def wrapper(*args, **kwargs):
        if not DATABASE_AVAILABLE:
            logger.warning("No database available")
            func = lambda *args, **kwargs: {}
            return func(*args, **kwargs)
        else:
            logger.debug("Calling function")
            return function(*args, **kwargs)
    return wrapper


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

    sort_field = "last_loaded"

    preference = "lowest"

    def __init__(self):
        if DATABASE_AVAILABLE:
            known_indices = client.indices.get_mapping().keys()
            if not APPLICATIONS_INDEX in known_indices:
                logger.info("No applications index found, creating now")
                client.indices.create(
                    index=APPLICATIONS_INDEX,
                    body={"mapping.total_fields.limit": 20000}
                    )
            if not CREDENTIALS_INDEX in known_indices:
                logger.info("No Credentials index found, creating now")
                client.indices.create(
                    index = CREDENTIALS_INDEX,
                    body={"mapping.total_fields.limit": 20000}
                )
        else:
            logger.info("No Database available, so API client functionality"
            "will be severely limited"
            )


    def prompt(self):
        """SHOULD BE SET BY INCA CLASS """
        pass

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

    @elasticsearch_required
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

    @elasticsearch_required
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
        credentials = self.load_credentials(app=app)
        if credentials:
            usable_credentials = credentials
        else:
            logger.warning("No usable credentials")
            return []

        logger.info("Starting client")
        if DATABASE_AVAILABLE == True and kwargs.get('database',True):
            for doc in self.get(credentials = usable_credentials, *args, **kwargs):
                doc = self._add_metadata(doc)
                self._verify(doc)
                self._save_document(doc)

        else:
            return [self._add_metadata(doc) for doc in self.get(*args, **kwargs)]

        logger.info('Done with retrieval')

    @elasticsearch_required
    def store_application(self, app_credentials, appname="default", retries=3,**kwargs):
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
        **kwargs
            additional fields

        Returns
        -------
        dictionary
            the ES document created or an empty dictionary on failure

        Notes
        -----
        `appname` is an internal indicator only. The name given to the app in
        the service (e.g. Twitter, Youtube, etcetera) is immaterial to this name.


        """
        logger.info("Adding new application: {appname}".format(**locals()))
        body  = {"credentials" : app_credentials, "other" : kwargs}
        try:
            attempt  = client.index(
                index = APPLICATIONS_INDEX,
                doc_type = self.service_name,
                id = appname,
                body = body
            )
        except ConnectionTimeout:
            retries -= 1
            logger.debug("Failed to index, retrying {retries} more times")
            if retries:
                time.sleep(1)
                return self.store_application(app_credentials,appname, retries, **kwargs)
            else:
                return {}
        except ConnectionError:
            logger.debug("Failed to connect, is Elasticsearch up?")
            return {}

        return self.load_application(appname)

    @elasticsearch_required
    def load_application(self, app="default",retries=3):
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
        try:
            app_credentials = client.get(
                index = APPLICATIONS_INDEX,
                doc_type = self.service_name,
                id = app
            )
        except ConnectionError:
            logger.warning("Could not connect to Elasticsearch, is it up?")
            return {}
        except ConnectionTimeout:
            retries -= 1
            logger.info("Connection timeout, retrieing {retries} more times").format(**locals())
            if retries:
                time.sleep(1)
                return self.load_application(app=app)
            else:
                return {}
        except NotFoundError:
            logger.warning("{app} was not found!".format(**locals()))
            return {}
        return app_credentials

    @elasticsearch_required
    def remove_application(self, app, retries=3):
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
        try:
            app_credentials = client.delete(
                index = APPLICATIONS_INDEX,
                doc_type = self.service_name,
                id = app
            )
        except ConnectionError:
            logger.warning("Could not connect to Elasticsearch, is it up?")
            return False
        except ConnectionTimeout:
            retries -= 1
            logger.info("Connection timeout, retrieing {retries} more times").format(**locals())
            if retries:
                time.sleep(1)
                return self.remove_application(app=app)
            else:
                return False
        except NotFoundError:
            logger.warning("{app} was not found!".format(**locals()))
            return False
        return True

    @elasticsearch_required
    def store_credentials(self, id, app='default', credentials={}, retries=3, **kwargs):
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
        consumer token and secret. By passing that dictionary tot this function,
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
        kwargs
            Additional information that may be provided for other purposes.
            Empty by default, saved as '_source.content':{kwargs}

        Returns
        -------
        boolean
            A True or False value indicating succesful saving.

        """
        doc = {'credentials': credentials, 'id':id, 'app':app,
                'content':kwargs,
                'last_loaded': datetime.datetime(year=1990,month=1,day=1).isoformat()}
        doctype = "{self.service_name}_{app}".format(**locals())

        app_available = self.load_application(app=app)
        if not app_available:
            logger.warning("App not available, check application name and retry")
            return {}

        try:
            credentials_stored = client.index(
                index = CREDENTIALS_INDEX,
                doc_type = doctype,
                id = id,
                body = doc
            )
            if credentials_stored['created']:
                logger.info("CREATED credentials [{id}] for {app}".format(**locals()))
            else:
                logger.info("UPDATED credentials {id} for {app}".format(**locals()))
        except ConnectionError:
            logger.warning("Could not connect to Elasticsearch, is it up?")
            return {}
        except ConnectionTimeout:
            retries -= 1
            logger.info("Connection timeout, retrieing {retries} more times").format(**locals())
            if retries:
                time.sleep(1)
                return self.store_credentials(id=id, app=app, credentials=credentials, retries=retries, **kwargs)
            else:
                return {}

        return self.load_credentials(app=app, id=id, update_last_loaded=False)

    @elasticsearch_required
    def load_credentials(self, app='default', id=None, update_last_loaded=True,retries=3):
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
            prepended with service name, i.e. "{service_name}_{app}" and
            retrieved from the database

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
        ordering = {'lowest':'asc','highest':'desc'}
        doctype  = "{self.service_name}_{app}".format(**locals())
        try:
            if id:
                credentials = client.get(
                    index=CREDENTIALS_INDEX,
                    doc_type=doctype,
                    id=id
                    )

            else:
                docs = client.search(index=CREDENTIALS_INDEX,
                              body={
                                  "sort": [
                                      {self.sort_field : {"order":ordering[self.preference]}}
                                      ],
                                  "size":1,
                                  "query":
                                  {"match":
                                   {"_type":
                                    doctype
                                   }
                                  }}).get('hits',{}).get('hits',[])
                if not docs:
                    logger.warning("No credentials found for {app}".format(**locals()))
                    return {}
                credentials = docs[0]
            if update_last_loaded:
                logger.debug("Updating last-loaded field")
                self.store_credentials(id=credentials['_id'],
                        doc_type = doctype,
                        app=app,
                        credentials = credentials['_source']['credentials'],
                        last_loaded=datetime.datetime.now().isoformat(),
                        content = credentials['_source']['content']
                        )

        except ConnectionTimeout:
            retries -= 1
            logger.info("Connection timeout when trying to retrieve, retrying {retries} more times")
            if retries:
                return self.load_credentials(app=app, id=id, retries=retries)
            else:
                return {}
        except ConnectionError:
            logger.warning("Unable to contact Elasticsearch, is it up?")
            return {}
        except NotFoundError:
            logger.warning("No credentials found")
            return {}
        except RequestError:
            logger.warning("You specified a sort field that does not exist!")
            return {}

        return credentials


    @elasticsearch_required
    def update_credentials(self, id, content={}, app='default',*args,**kwargs):
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

        Returns
        -------
        boolean
            Indicates the success/failure of the update

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
        old_credentials = self.load_credentials(app=app, id=id)
        if not old_credentials:
            logger.warning("Failed to update credentials {id} for app {app}".format(**locals()))
            return False
        content.update(**kwargs)
        if not 'credentials' in content:
            credentials = old_credentials['_source']['credentials']
        else:
            logger.debug("Updating credentials information as well")
            credentials=content["credentials"]
        updated = self.store_credentials(app=app, id=id, credentials=credentials,**content)
        return updated

        #TODO IMPLEMENT remove credentials

        #TODO: IMPLEMENT DECENTRALIZED POSTPONE
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
            now = datetime.datetime.now()
            if until:
                waittime = until - now
            else:
                waittime = datetime.timedelta(
                            seconds=seconds,
                            minutes=minutes,
                            hours = hours,
                            days = days
                            )
            logger.info("Delaying for {waittime}".format(**locals()))
            time.sleep(waittime)
            for d in self.run(*args, **kwargs):
                yield d
