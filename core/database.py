'''
Here you find CRUD functionality. 

This module provides database access objects. The idea is
that all database specific functionality is in this document alone. Other
classes and functions should interact with the database only through 
functionality provided here. 
'''


import logging
import json
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.exceptions import ConnectionTimeout
import configparser

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))

logger = logging.getLogger(__name__)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

client = Elasticsearch(
    host=config.get('elasticsearch','%s.host' %config.get('inca','dependencies')),
    port=int(config.get('elasticsearch','%s.port'%config.get('inca','dependencies') ))
)   # should be updated to reflect config
elastic_index  = config.get("elasticsearch","document_index")

# initialize mappings if index does not yet exist
try:
    if not elastic_index in client.indices.get_aliases().keys():
        client.indices.create(elastic_index, json.load(open('schema.json')))
except:
    raise Exception("Unable to communicate with elasticsearch")

def get_document(doc_id):
    if not check_exists(doc_id):
        logger.debug("No document found with id {document_id}".format(**locals()))
        return {}
    else:
        document = client.get(elastic_index, doc_id)
    return document

def check_exists(document_id):
    index = elastic_index
    try:
        retrieved = client.get(elastic_index,document_id)
        logger.debug('elastic_index {index} - document [{document_id}] found, return document'.format(**locals()))
        return True, retrieved
    except NotFoundError:
        logger.debug('elastic_index {index} - document [{document_id}] NOT found, returning false'.format(**locals()))
        return False, {}
    # TODO: ADD TIMEOUT HANDLER
    except:
        logger.warning('unable to check for documents in elasticsearch elastic_index [{elastic_index}]'.format(**{'elastic_index':elastic_index}))
    
        
def update_document(document, force=False):
    '''
    Documents should usually only be appended, not updated. as such.

    input documents should be elasticsearch results with added fields. 

    '''
    exists, old_document = check_exists(document['_id'])
    if exists and not force:
        logging.debug('updating existing document {old_document[_id]}'.format(**locals()))
        document['_source'].update(old_document['_source'])
        document = _remove_dots(document)
        client.update(index=elastic_index,
                      doc_type=document['_type'],
                      id=document['_id'],
                      body={'doc':document['_source']}
        )
    elif exists and force:
        client.delete(index=elastic_index,
                      doc_type=old_document['_type'],
                      id=old_document['_id'])
        
        logging.info('FORCED UPDATE of {old_document[_id]}'.format(**locals()))
        document = _remove_dots(document)
        client.index(index=elastic_index,
                      doc_type=old_document['_type'],
                      id=old_document['_id'],
                      body={'doc':document['_source']}
        )
    else:
        logging.debug('No existing document found for {document}, defering to insert function')
        insert_document(document)
    pass

def delete_document(document_id):
    ''' delete a document, with parameters '''
    found, document = check_exists(document_id)
    if not found: logger.debug('{document_id} does not exist'.format(**locals()))
    response = client.delete(index=elastic_index, id=document['_id'], doc_type=document['_type'])
    return True

def insert_document(document, custom_identifier=''):
    ''' Insert a new document into the default index '''
    document = _remove_dots(document)
    if not custom_identifier:
        try:
            doc = client.index(index=elastic_index, doc_type=document['doctype'], body=document)
        except ConnectionTimeout:
            insert_document(document, custom_identifier)
    else:
        try:
            doc = client.index(index=elastic_index, doc_type=document['doctype'], body=document, id=custom_identifier)
        except ConnectionTimeout:
            insert_document(document, custom_identifier)
    logger.debug('added new document [{doc[_id]}], content: {document}'.format(**locals()))
    return doc["_id"]

def update_or_insert_document(document):
    ''' Check whether a document exists, update if so '''
    if '_id' in document.keys():
        exists, document = check_exists(document['_id'])
        if exists:
            return update_document(document)
    return insert_document(document)

def _remove_dots(document):
    ''' elasticsearch is allergic to dots like '.' in keys.
    if you're not carefull, it may choke!
    '''
    for k,v in document.items():
        if '.' in k:
            document[k.replace('.','_')]=document.pop(k)
        if type(v)==dict:
            document[k.replace('.','_')]= _remove_dots(v)
    return document
