'''
This file provides the base-class for API clients
'''
from scraper_class import Scraper
from clients._general_utils import *

class Client(Scraper):
    '''Clients provide access to APIs. Clients sublcasses should provide the following functionality

    service_name is extracted from the first, underscore seperated, part of the class name (!)
        i.e., twitter_get_timeline => self.service_name = "twitter"

    add_credential: method
        Take the required steps to get new credential, yield {id: credentials} dictionary consumable by the 'get' method

    credential_usage_condition: string, (default=None)
        condition to use a credential

    get: method
        should expect a 'credentials' argument that reflects the credentials stored by add_credentials
        Get new content, probably defined in the subclass of a service subclass. i.e.:
        class twitter(Client)
        class get_timeline(twitter)

    '''

    service_name               = self.__name__.split('_')[0]
    credential_usage_condition = None

    def run(self,pool='default', *args, **kwargs):
        '''Get stuff from the client through Scraper.run() method, by adding credential keyword'''
        credentials = get_credentials(self.service_name, pool_name=pool, filter=self.credential_usage_condition)
        usable_credentials = {credentials['_id']:credentials['_source'].get('credentials')}
        return Super(Client, self).run(credentials=usable_credentials, *args, **kwargs)
