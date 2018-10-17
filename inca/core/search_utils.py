'''
This file provides basic search functionality for the INCA database.
'''
from .database import client as _client
from .database import scroll_query as _scroll_query
from .database import elastic_index as _elastic_index
from .database import DATABASE_AVAILABLE as _DATABASE_AVAILABLE
from .database import delete_doctype, delete_document, insert_document, insert_documents
import logging as _logging
from .basic_utils import dotkeys as _dotkeys
import _datetime as _datetime
import json as _json
from collections import defaultdict

_logger = _logging.getLogger("INCA")

def list_doctypes():
    if not _DATABASE_AVAILABLE:
        _logger.warning("Could not list documents: No database instance available")
        return []

    existing_doctypes = _client.search(_elastic_index, body = {"size": 0, "aggs":{"doctypes":{"terms":{"field":"doctype", "size":1000}}}})["aggregations"]["doctypes"]["buckets"]
    overview  = {}
    for item in existing_doctypes:
        overview[item['key']] = item['doc_count']
    return overview


def doctype_generator(doctype):  
    query = {'query':{'term':{'doctype':doctype}}}
    for num, doc in enumerate(_scroll_query(query)):
        if not _DATABASE_AVAILABLE:
            _logger.warning("Could not get documents: No database instance available")
            break
        if not num%100: _logger.info("returning {num}".format(**locals()))
        yield doc

def document_generator(query="*"):
    """A generator to get results for a query

    Parameters
    ----
    query : string (default="*") or dict
        A string query specifying the documents to return or a dict
        that is a elasticsearch query

    Yields
    ----
    dict representing a document
    """
    if not _DATABASE_AVAILABLE:
        _logger.warning("Unable to generate documents, no database available!")
    else:
        if query == "*": _logger.info("No query specified, returning all documents")
        if type(query) == str:
            _logger.info("String input: searching for {query}".format(query=query))
            es_query = {"query":{"bool":{"must":{"query_string":{"query":query}}}}}
            _logger.debug("query: {es_query}".format(es_query=es_query))
        elif type(query) == dict:
            _logger.info("Dict input: using input as ES query")
            _logger.debug("query: {query}".format(query=_json.dumps(query, indent=2)))
            es_query = query
        else:
            _logger.warning("Unknown input")
            es_query = False
        if es_query:
            # total = _client.search(_elastic_index, body=es_query, size=0)['hits']['total']
            for doc in _scroll_query(es_query):
                yield doc


def doctype_first(doctype, num=1, by_field="META.ADDED",query=None):
    '''Returns the first document of a given doctype

    Input
    ---
    doctype: string
        The document type you whish to retrieved
    num: int
        The number of documents to retrieve
    by_field: string
        The _datetime field by which to determine the
        first document
    query : string (default None)
        An Elasticsearch string query to filter results.
        Example: query="user.screen_name:google
    '''
    if not _DATABASE_AVAILABLE:
        _logger.warning("Could not get first document: No database instance available")
        return []

    body = {
        "sort": [
            {by_field : {"order":"asc"}}
            ],
        "size":num,
        "query":
        {"term":
         {"doctype":
          doctype
         }
        }}

    if query:
        _logger.debug("adding string query: {query}".format(**locals()))
        body['query'] = {'query_string':{'query': query}}

    docs = _client.search(index=_elastic_index,

                  body={
                      "sort": [
                          {by_field : {"order":"asc"}}
                          ],
                      "size":num,
                      "query":
                        { "term":
                          { "doctype": doctype
                          }
                      }}).get('hits',{}).get('hits',[""])

    return docs

def doctype_last(doctype,num=1, by_field="META.ADDED", query=None):
    '''Returns the last document of a given doctype

    Input
    ---
    doctype: string
        The document type you whish to retrieved
    num: int
        The number of documents to retrieve
    by_field: string
        The _datetime field by which to determine the
        last document
    query : string (default None)
        An Elasticsearch string query to filter results.
        Example: query="user.screen_name:google"
    '''
    if not _DATABASE_AVAILABLE:
        _logger.warning("Could not get last documents: No database instance available")
        return []
    
    body = {
        "sort": [
            {by_field : {"order":"desc"}}
            ],
        "size":num,
        "query":
        {"term":
         {"doctype":
          doctype
         }
        }}

    if query:
        _logger.debug("adding string query: {query}".format(**locals()))
        body['query'] = {'query_string':{'query': query}}

    docs = _client.search(index=_elastic_index,
                  body={
                      "sort": [
                          { by_field : {"order":"desc"}}
                          ],
                      "size":num,
                      "query":
                      { "term":{
                        "doctype":
                        doctype
                        }
                      }}).get('hits',{}).get('hits',[""])

    return docs

def doctype_examples(doctype, field=None, seed=42, num=10):
    if not _DATABASE_AVAILABLE:
        _logger.warning("Could not get example documents: No database instance available")
        return []  
    docs = _client.search(index=_elastic_index, body={
        'size':num,
        "query": {
            "function_score": {
                    "query": {"term":
                                { "doctype": doctype
                                }
                            }
                        ,
                "functions": [
                    {
                        "random_score": {
                            "seed": seed
                            }
                        }
                    ]
                }}
    })
    if not field:
        return docs['hits']['hits']
    elif type(field)==str:
        return [_dotkeys(doc,field) for doc in docs['hits']['hits']]
    else:
        return [{fi:_dotkeys(doc,fi) for fi in field} for doc in docs['hits']['hits']]

def doctype_fields(doctype):
    '''
    returns a summary of fields for documents of `doctype`:
    field : type - count (coverage)

    note:
        As elasticsearch does not natively support an 'all fields' query,
        this function runs a 1000 document sample and takes the union of
        found keys as a proxy of fields shared by all documents.
    '''
    if not _DATABASE_AVAILABLE:
        _logger.warning("Could not get document information: No database instance available")
        return []

    doc_num   = _client.search(index=_elastic_index, body={'query':{"term":{"doctype":doctype}}})['hits']['total']
    mappings = _client.indices.get_mapping(_elastic_index).get(_elastic_index,{}).get('mappings',{}).get('doc',{}).get('properties', {})
    coverage = {key:_client.search(_elastic_index,body={'query': {'bool':{'filter':[{'exists':{'field':key}},{'term':{"doctype":doctype}}]}}}).get('hits',{}).get('total',0) for key in mappings.keys() if key!="META"}
    summary = {k:{'coverage':coverage.get(k,'unknown')/float(doc_num),'type':mappings[k].get('type','unknown')} for
               k in mappings.keys() if k!="META" and coverage.get(k, 'unknown') != 0}
    return summary

def missing_field(doctype=None, field='_source', stats_only=True):
    if not _DATABASE_AVAILABLE:
        _logger.warning("Could not get documents missing a field: No database instance available")
        return []
    query = {'query':{'bool':{'must_not':{'exists':{'field':field}}}}}
    if not doctype:
        result = _client.search(_elastic_index, body=query)
    else:
        result = _client.search(_elastic_index, doctype, body=query)
    if not stats_only:
        return result['hits']['hits']
    else:
        #total = doctype and _client.search(_elastic_index, doctype)['hits']['total'] or _client.search(_elastic_index)['hits']['total']
        stats = {
            'doctype' : doctype and doctype or '*',
            'field' : field,
            'missing': result['hits']['total'],
            #'total'  : total,
            'percentage_missing' : ((result['hits']['total'])/(total*1.))*100
        }

        return stats
def doctype_inspect(doctype):
    '''Show some information about documents of a specified type

    Parameters
    ----------
    doctype : string
        string specifying the doctype to examine (see list_doctypes for available documents)

    Returns
    -------
    dictionary
        summary of documents of the specified type:
            total collected : integer
                the amount of documents of this type (approximation)
            first_collected : _datetime
                the minimal 'META.ADDED' field of these documents, which
                specifies the oldest documents
            last_collected : _datetime
                the maximum 'META.ADDED' field of these documents which
                specifies when the last document of this type was collected
            keys : dictionary
                <keyname> : dictionary
                    coverage : float
                        the proportion of documents that have this key
                    type     : string
                        the elasticsearch index type of this field

    '''

    firstdocs = doctype_first(doctype, by_field="META.ADDED")
    lastdocs  = doctype_last(doctype, by_field="META.ADDED")

    summary = dict(
        total_collected = _client.search(index=_elastic_index, body={'query':{"term":{"doctype":doctype}}})['hits']['total'],
        first_collected = firstdocs and firstdocs[0].get('_source',{}).get('META',{}).get("ADDED",None) or None,
        last_collected = lastdocs and lastdocs[0].get('_source',{}).get('META',{}).get("ADDED",None),
        keys=doctype_fields(doctype)
    )


    return summary

def list_apps(service_name=None):
    """Lists the API apps registered in this INCA instance

    Parameters
    ----
    service_name : string (default=None)
        The name of the service, such as 'twitter', 'facebook' or 'google'.If
        no name is provided, apps for all services are returned

    Returns
    ----
    Dictionary or list
        When a service_name is provided, a list of apps registered for this
        service are returned. Otherwise, a dictionary with the structure
        `{service_name : [app1, app2, app3]}` are returned.

    """
    res = _client.search(index='.apps', doc_type=service_name, size=10000)
    get_num_credentials = lambda app: _client.search(
        index='.credentials',
        doc_type=app['_type']+"_"+app['_id'],
        size=0)['hits']['total']
    apps = {}
    for app in res['hits']['hits']:
        if service_name and service_name!=app['_type']: continue
        app_ob = {'name':app['_id'],'credentials': get_num_credentials(app)}
        if not apps.get(app['_type']):
            apps[app['_type']] = [app_ob]
        else:
            apps[app['_type']].append(app_ob)
    if service_name:
        return apps.get(service_name,[])
    return apps

def list_credentials(service_name, app_name):
    """Lists the credentials associated with a registered app

    Parameters
    ----
    service_name : string
        a string specifying the name of the service the app targets, such as
        'twitter','facebook' or 'google'
    app_name : string
        a string with the internal application name

    Returns
    ----
    A list of credentials belonging to the application
    """
    #app_type = service_name + "_" + app_name
    #credentials = _client.search(index = ".credentials", doc_type=app_type)
    #return credentials['hits']['hits']
