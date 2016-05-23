'''

This module provides database access objects. The idea is
that all database specific functionality is in this document alone. Other
classes and functions should interact with the database only through 
functionality provided here. 

TODO: factor in settings 

'''


import logging
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search, Q

logger = logging.getLogger(__name__)

client = Elasticsearch() # should be updated to reflect config
elastic_index  = 'inca'          # should be updated to reflect config
elastic_doctype = 'nl_doc'

''' DEPRECATED, MOVING TO ELASTICSEARCH 
logger = logging.getLogger(__name__)

client = pymongo.MongoClient()

document_collection = client.inca.documents

user_collection     = client.inca.users
'''


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
    Documents should usually only be appended, not updated. as such
    '''
    exists, old_document = check_exists(document['_id'])
    if exists and not force:
        logging.debug('updating existing document {old_document[_id]}'.format(**locals()))
        document.update(old_document['_source'])
        client.update(index=elastic_index,
                      doc_type=document['_type'],
                      id=document['_id'],
                      body={'doc':document}
        )
    elif exists and force:
        logging.info('FORCED UPDATE of {old_document[_id]} from {document} to {old_document}'.format(**locals()))
        client.update(index=elastic_index,
                      doc_type=old_document['_type'],
                      id=old_document['_id'],
                      body={'doc':document}
        )
    else:
        logging.debug('No existing document found for {document}, defering to insert function')
        insert_document(document)
    pass

def delete_document(document_id):
    pass

def insert_document(document):
    return "_id"

def update_or_insert_document(document):
    return "_id"
