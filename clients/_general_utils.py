'''
This file provides shared infrastructure for API clients.

Credential pools: named lists of credentials for a given API, CRUD functionality
Mapping : for storing pools in elasticsearch

'''

from core.database import client
import datetime
import logging
from elasticsearch import NotFoundError, TimeoutError

logger = logging.getLogger(__name__)


def put_credentials(service_name, pool_name='default', credentials, id, force=False):
    '''

    Parameters
    ----------
    service_name: string
        Service for which credentials are used.
    pool_name: string (default='default')
        Name of pool.
    credentials: dict
        Dictionary containing the credentials required for the given service
    id: string
        string that serves as an id for the credentials (should be unique to service)
    force: bool
        Boolean indicating whether existing credentials should  be overwritten

    Returns
    -------
    Boolean
        Represents the success state of the put request
    '''
    try:
        credentials = client.get('credentials', doc_type=service_name , id=id )
        logger.info("Updating existing credentials [{id}]".format(**locals()))
        if not pool_name in credentials['_source']['pools']:
            credentials['_source']['pools'].append(pool_name)
            client.update(index='credentials', doc_type=service_name, id=id, body=credentials['_source'])
            logger.info('Added credentials {id} to {service_name}:{pool_name}'.format(**locals()))
        elif not force:
            logger.info("Credentials are already in this pool! Put request ignored... (use force to override)")
            return False
        elif force:
            client.index(index='credentials', doc_type=service_name, id=id, body=credentials['_source'])
    except NotFoundError:
        logger.info('Credentials do not yet exist in credentialstore')
        credentials = {
            "service" : service_name,
             "pools"  : [pool_name],
            "credentials" : credentials
        }
        client.index(index="credentials", doc_type=service_name, id=id, body=credentials)
    except TimeoutError:
        logger.warn("elasticsearch timed out, retrying... ")
        return put_credentials(service_name, pool_name, credentials, id, force)
    return True

def delete_credentials(service_name, pool_name, id):
    '''

    Parameters
    ----------
    service_name: string
        The service for which credentials are used (e.g. Twitter, Facebook, Github).
    pool_name: string
        The pool name, used to distinguish credentials collected for different purposes
    id
        The id of the credentials to remove from this pool. Credentials without any pool are deleted.

    Returns
    -------
    Boolean indicating success
    '''

def get_credentials(service_name, pool_name='default', filter=None):
    '''get credentials from a specified service pool

    Parameters
    ---
    service_name : string
        Service for which credentials are used. E.g. Twitter, Facebook, Github
    pool_name : string (default='default')
        Pool of credentials to use, which may be specific (such as credentials collected
        for a specific survey)
    filter: string (default=None)
        Elasticsearch string-query with additional filtering option.
        E.g. 'last_response.rate_limit_remaining:>=1'
    '''
    base_query : "service:'{service_name}' AND pool:'{pool_name}'".format(**locals())
    if filter:
        full_query= {
            'query':
                {'string_query': {'query':base_query} },
            'filter':
                {'string_query'}: {'query':filter}
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
        return []

def get_credentials_by_id(id):
    '''

    Parameters
    ----------
    id: string
        the unique id associated with the credentials that should be returned

    Returns
    -------
    credentials: dict
        dictionary typed credentials object, with service specific credentials in the 'credentials' key
    '''
    return client.get(index='credentials', id=id)