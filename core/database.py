'''
Here you find CRUD functionality.

This module provides database access objects. The idea is
that all database specific functionality is in this document alone. Other
classes and functions should interact with the database only through
functionality provided here.
'''


import logging
import json
import csv
from elasticsearch import Elasticsearch, NotFoundError, helpers
from elasticsearch.exceptions import ConnectionTimeout
import time
from datetime import datetime
import configparser
import requests
from celery import Task
import os

config = configparser.ConfigParser()
config.read('settings.cfg')

logger = logging.getLogger("INCA"+__name__)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

try:
    client = Elasticsearch(
        host=config.get('elasticsearch','%s.host' %config.get('inca','dependencies')),
        port=int(config.get('elasticsearch','%s.port'%config.get('inca','dependencies') )),
        timeout=60
    )   # should be updated to reflect config
    elastic_index  = config.get("elasticsearch","document_index")
    DATABASE_AVAILABLE = True

    # initialize mappings if index does not yet exist
    try:
        #if not elastic_index in client.indices.get_aliases().keys():
        if not client.indices.exists(elastic_index):
            # TODO re-activate using the schema, now disabled in order to make existing code
            # work with ES 5 (at least on my system)
            # client.indices.create(elastic_index, json.load(open('schema.json')))
            client.indices.create(elastic_index)
    except Exception as e:
        raise Exception("Unable to communicate with elasticsearch, {}".format(e))
except:
    logger.warning("No database functionality available")
    DATABASE_AVAILABLE = False



def get_document(doc_id):
    if not check_exists(doc_id)[0]:
        logger.debug("No document found with id {doc_id}".format(**locals()))
        return {}
    else:
        document = client.get(elastic_index, doc_id)
    return document

def check_exists(document_id):
    if not DATABASE_AVAILABLE: return False, {}
    index = elastic_index
    try:
        retrieved = client.get(elastic_index,document_id)
        logger.debug('elastic_index {index} - document [{document_id}] found, return document'.format(**locals()))
        return True, retrieved
    except NotFoundError:
        logger.debug('elastic_index {index} - document [{document_id}] NOT found, returning false'.format(**locals()))
        return False, {}
    # TODO: ADD TIMEOUT HANDLER
    except ConnectionTimeout:
        logger.warning('unable to check for documents in elasticsearch elastic_index [{elastic_index}]'.format(**{'elastic_index':elastic_index}))
        time.sleep(1)
        return check_exists(document_id)

def update_document(document, force=False, retry=0, max_retries=10):
    '''
    Documents should usually only be appended, not updated. as such.

    input documents should be elasticsearch results with added fields.

    input
    ---
    document: dict
        An elasticsearch document
    force: boolean
        Indicates whether the document should replace (true) or only
        expand existing documents (false). Note that partial updates
        are not supported when forcing.
    retry (optional): integer [default=0]
        counter of the number of tries
    max_retries (optional): integer [default=10]
        number of attempts to insert documents. Compared to retry integer.

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
        #client.delete(index=elastic_index,
        #              doc_type=old_document['_type'],
        #              id=old_document['_id'])
        #
        logging.info('FORCED UPDATE of {old_document[_id]}'.format(**locals()))
        document = _remove_dots(document)
        try:
            client.index(index=elastic_index,
                         doc_type=old_document['_type'],
                         id=old_document['_id'],
                         body=document['_source']
            )
        except Exception as e:
            if retry < max_retries:
                logging.warning("FAILED TO RE-INSERT DOCUMENT {document[_id]}, {e} retrying".format(**locals()))
                update_document(document, force=force, retry=retry+1, max_retries=max_retries)
            else:
                raise e
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

def delete_doctype(doctype):
    '''Delete all documents of a given type'''
    for doc in scroll_query({'query':{'bool':{'filter':{'match':{'_type':doctype}}}}}):
        delete_document(doc['_id'])
    return True

def insert_document(document, custom_identifier=''):
    ''' Insert a new document into the default index '''
    document = _remove_dots(document)
    if not custom_identifier:
        try:
            doc = client.index(index=elastic_index, doc_type=document['doctype'], body=document)
        except ConnectionTimeout:
            doc = {'_id':insert_document(document, custom_identifier)}
    else:
        try:
            doc = client.index(index=elastic_index, doc_type=document['doctype'], body=document, id=custom_identifier)
        except ConnectionTimeout:
            doc= {'_id':insert_document(document, custom_identifier)}
    logger.debug('added new document, content: {document}'.format(**locals()))
    return doc["_id"]

def update_or_insert_document(document, force=False):
    ''' Check whether a document exists, update if so '''
    if '_id' in document.keys():
        exists, document = check_exists(document['_id'])
        if exists:
            return update_document(document, force=force)
    return insert_document(document)

def remove_field(query, field):
    batch = []
    for num, document in enumerate(scroll_query(query)):
        try:
            document['_source'].pop(field)
        except:
            logger.info('skipping {document[_id]}'.format(**locals()))
            continue
        try: document['_source']['META'].pop(field)
        except: pass # This field could be missing
        batch.append(document)
        if (num+1) % 50 and batch:
            logger.info("upserting batch %s" %((num+1) % 50 ))
            bulk_upsert().run(batch)
            batch = []
    if batch: # in case of leftovers
        bulk_upsert().run(batch)

class bulk_upsert(Task):
    '''Processers can generate far more updates than elasticsearch wants to handle.
       Bulk_upsert reduces the load on elasticsearch by enabeling multiple documents
       to be updated together, reducing the amount of queries.
    '''
    def run(self, documents):
        logger.debug(documents)
        return helpers.bulk(client, documents)


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

def scroll_query(query,scroll_time='10m', log_interval=None):
    scroller = client.search(elastic_index,
                             body=query,
                             scroll=scroll_time,
                             # search_type='scan' # DOES NOT SEEM TO BE SUPPORTED BY CURRENT ES-VERSION
    )
    sid  = scroller['_scroll_id']
    size = scroller['hits']['total']
    tot_size = size # keep total size for logging
    logger.info('scrolling through {size} results'.format(**locals()))
    at_num = 0
    if not log_interval:
        log_interval = min(tot_size / 10000, 100)
    while size > 0 :
        try:
            page = client.scroll(scroll_id = sid,
                             scroll = scroll_time)
        except ConnectionTimeout:
            time.sleep(1)
            continue
        sid = page['_scroll_id']
        size = len(page['hits']['hits'])

        for doc in page['hits']['hits']:
            at_num+=1
            if log_interval and not (at_num % ( int(log_interval) or 2)):
                pos = (at_num/float(tot_size))*100
                elements = '='* int(30*(pos)/100)
                logger.info("At  {pos:10.2f}% [{elements:30.30}] {at_num:10} of {tot_size}".format(**locals()))
            yield doc


#####################
#
# Database backup functionality
#
######################


def create_repository(location):
    '''Creates a repository called 'inca_backup', which is required
    to save snapshots. The location must be added to the `path.repo` field
    of elasticsearch.yml (generally located at the elasticsearch folder)

    Parameters
    ----------
    location : string
        The location of the specified backup path, should match
        the "path.repo" argument in the "elasticsearch.yml" file

    Returns
    -------
    Dictionary
        Dictionary with ES response to request

    Example
    -------
    ```bash
    echo "path.repo: /path/to/inca/backup" >> /path/to/elasticsearch/config/elasticsearch.yml
    ```
    ```python
    import inca
    inca.core.database.create_repository("/path/to/inca/backup")
    >>> {'acknowledged': True}
    inca.core.database.create_backup("arbitrary_name")
    >>> {'accepted': True}
    ```

    Notes
    -----
    The repository location must match the `path.repo` argument in the
    `elasticsearch.yml` file, generally located in the .../elasticsearch/config
    path. Elasticsearch must be restarted after the `path.repo` is set or changed.
    '''

    body = {
                  "type": "fs",
                  "settings": {
                            "compress": "true",
                            "location": location
                          }
                }
    return client.snapshot.create_repository('inca_backup',body=body)

def check_snapshot_settings(snapshot):
    return client.snapshot.status(snapshot)

def list_backups():
    response = requests.get('http://%s:%s/_snapshot/inca_backup/*' %(config.get('elasticsearch','%s.host' %config.get('inca','dependencies')),
                                                                     config.get('elasticsearch','%s.port' %config.get('inca','dependencies'))))
    return response.json()

def create_backup(name):
    """create a backup of the Elasticsearch indices

    Saves a named backup to the specified backup directory. This requires
    an inca repository to be initialized using the `create_repository` function.
    That function is required to run only once after setting a (new) path.repo
    value.

    Parameters
    ----------
    name : str
        A string specifying a designation for the snapshot. Usefull
        for selectively loading a backup.

    Returns
    -------
    dict
        A dictionary with the elasticsearch response

    Notes
    -----
    For this function to run, a 'inca_backup' repository must be instantiated.
    Please see the `create_repository` function.

    Also note that the function returns before the backup process is completed.
    Avoid shutting down elasticsearch before the backup has been fully written
    to disk.

    """
    body = {
          "indices": "*",
          "ignore_unavailable": "false",
          "include_global_state": True
        }

    return client.snapshot.create(repository='inca_backup', snapshot=name,body=body)

def restore_backup(name):
    if name in [item['snapshot'] for item in list_backup()]:
        client.indices.close('inca')
        client.snapshot.restore(repository='inca_backup', snapshot=name)

def export_doctype(doctype):
    if not 'exports' in os.listdir('.'):
        os.mkdir('exports')
    for doc in scroll_query({'query':{'match':{'doctype':doctype}}}):
        outpath = os.path.join('exports',doctype)
        if doctype not in os.listdir('exports'):
            os.mkdir(outpath)
        with open(os.path.join('exports', doctype, '%s.json' %doc['_id']),'w') as f:
            f.write(json.dumps(doc))

def export_csv(query, keys = ['doctype','publication_date','title','byline','text']):
    '''
    Takes a dict with an elastic search query as input and exports the given keys to a csv file

    input:
    ---

    query: dict
        An ElasticSearch query, e.g. query = {'query':{'match':{'doctype':'nu'}}}
    keys: list
        A list of keys to be mapped to columns in the csv file. Often used keys include ['doctype', 'publication_date', 'text', 'feedurl', 'teaser', 'title', 'htmlsource', 'byline', 'url']
    '''

    if not 'exports' in os.listdir('.'):
        os.mkdir('exports')
    with open(os.path.join('exports',"{}.csv".format(datetime.now().strftime("%Y%m%d_%H%M%S"))),'w') as f:
        writer=csv.writer(f)
        headerrow = keys
        writer.writerow(headerrow)
        for doc in scroll_query(query):
            row = [doc['_source'][k] for k in keys]
            writer.writerow(row)

def import_documents(source_folder, force=False):
    for input_file in os.listdir(source_folder):
        update_or_insert_document(json.load(open(input_file)), force=force)
