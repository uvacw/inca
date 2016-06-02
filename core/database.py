'''
Here you find CRUD functionality. 

This module provides database access objects. The idea is
that all database specific functionality is in this document alone. Other
classes and functions should interact with the database only through 
functionality provided here. 

TODO: factor in settings 

'''


import logging
from settings import get_config
from elasticsearch import Elasticsearch, NotFoundError

config = get_config('Production')
logger = logging.getLogger(__name__)

client = Elasticsearch(
    host=config.ELASTIC_HOST,
    port=config.ELASTIC_PORT
)   # should be updated to reflect config
elastic_index  = config.ELASTIC_DATABASE    # should be updated to reflect config 

if not elastic_index in client.indices.get_aliases().keys():
    client.indices.create('inca', json.load(open('schema.json')))

def check_exists(document_id):
    index = elastic_index
    try:
        retrieved = client.get(elastic_index,document_id)
        logger.debug('elastic_index {index} - document [{document_id}] found, return document'.format(**locals()))
        return True, retrieved
    except NotFoundError:
        logger.debug('elastic_index {index} - document [{document_id}] NOT found, returning false'.format(**locals()))
        return False, {}
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
        logging.info('FORCED UPDATE of {old_document[_id]} from {document} to {old_document}'.format(**locals()))
        document = _remove_dots(document)
        client.update(index=elastic_index,
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
        doc = client.index(index=elastic_index, doc_type=document['doctype'], body=document)
    else:
        doc = client.index(index=elastic_index, doc_type=document['doctype'], body=document, id=custom_identifier)
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
