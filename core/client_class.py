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

    add_credential: method
        Take the required steps to get new credential, returns (id, credentials) tuple consumable by the 'get' method

    credential_usage_condition: string, (default=None)
        condition to use a credential

    get: method
        should expect a 'credentials' argument that reflects the credentials stored by add_credentials
        Get new content, probably defined in the subclass of a service subclass. i.e.:
        class twitter(Client)
        class get_timeline(twitter)

    '''

    service_name               = "UNKNOWN"
    def credential_usage_condition(self):
        return None

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


    def new_credential(self, CLI=True, premade=None, force=False, pool_name='default'):
        """

        Parameters
        ----------
        CLI: bool (default=True)
            Parameter specifying whether to use a commandline interface implementation or WUI
        premade: dict (default=None)
            premade is an optional shortcut that can be used to supply pre-collected credentials

        Returns
        -------
        bool

        """
        if not premade:
            new_credentials = self.add_credentials()
        else:
            new_credentials = premade
        put_credentials(self.service_name,
                        pool_name=pool_name,
                        id=new_credentials[0],
                        credentials=new_credentials[1]
                        )

    def update_last(self,id,last_content):
        """
        Updates credentials last use information for rate-limiting purposes

        Parameters
        ----------
        id
        last_content

        Returns
        -------
        None
        """
        update_credentials_last(id, last_response=last_content)

    def postpone(self, delaytime, *args, **kwargs):
        """

        Parameters
        ----------
        delaytime: int
            time in seconds to delay function
        args:
            arguments to be passed to self.run after delaytime
        kwargs:
            keyword arguments to be passed to self.run after delaytime

        Returns
        -------

        """
        logger.info("delaying for {delaytime} seconds".format(**locals()))
        if config.get('inca','local_only') == "True":
            time.sleep(delaytime)
            self.run(*args, **kwargs)
        else:
            self.delay(args, kwargs, countdown=delaytime)