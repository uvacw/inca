'''
This file provides shared infrastructure for API clients.

Credential pools: named lists of credentials for a given API, CRUD functionality
Mapping : for storing pools in elasticsearch

'''

from core.database import client
import datetime
import logging

logger = logging.getLogger(__name__)


def put_credentials(service_name, pool_name='default', credentials, identifier, force=False):
    '''

    Parameters
    ----------
    service_name: string
        Service for which credentials are used.
    pool_name: string (default='default')
        Name of pool.
    credentials: dict
        Dictionary containing the credentials required for the given service
    identifier: string
        string that serves as an id for the credentials (should be unique to service)
    force: bool
        Boolean indicating whether existing credentials should  be overwritten

    Returns
    -------
    Boolean
        Represents the success state of the put request
    '''
    if not force:
        query = "service:'{service_name}' AND pool:'{pool_name}' AND _id:'{identifier}'".format(**locals())
        exists = client.search("credentials",body={"query":{"string_query":{"query":query}}})
        if identifier in [hit.get('_id','') for hit in exists.get('hits',{}).get('hits',[])]:
            logger.info("credentials already exist!")
            return False
    update = {
        service: service_name,
        pool: pool_name,
        credentials: credentials,
        ADDED: datetime.datetime.now()
        last_response: {}
    }
    client.index('credentials', doc_type=service_name, body=update)
    logger.info("added new credentials to {service_name}:{pool_name}".format(**locals()))
    return True

def delete_credentials(service_name, )

def get_credentials(service_name, pool_name='default', filter=None):
    '''get credentials from a specified service pool

    Parameters
    ---
    service_name : string
        Service for which credentials are used. E.g. Twitter, Facebook, Github
    pool_name : string (default='default')
        Pool of credentials to use, which may be specific (such as credentials collected
        for a specific survey)
    filter: dict (default=None)
        query with additional filtering option.
        E.g. {'last_response.rate_limit_remaining':{'gte':0}}
    '''
    base_query : "service:'{service_name}' AND pool:'{pool_name}'".format(**locals())
    if filter:
        full_query= {
            'query':
                {'string_query': {'query':base_query} },
            'filter':filter
        }
    else:
        full_query= {
            'query':
                {'string_query': {'query': base_query}}
        }
    try:
        return client.search('credentials',body=full_query)['hits']['hits']
    except Exception as e:
        info.warn("get_credentials failed {e}")
        return {}

