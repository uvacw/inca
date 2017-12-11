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
from urllib.parse import quote_plus
from hashlib import md5

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
            client.indices.create(elastic_index, json.load(open('schema.json')))
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
    ''' delete a document

    Parameters
    ----
    document_id : string, dict or list
        A string containing the document id. Alternatively, a document retrieved
        from elasticsearch from which the `_id` field can be extracted. If a
        list, it is assumed each element is an id or document to be deleted.

    Returns
    ----
    Bool
        Whether the document was deleted

    '''
    if type(document_id) == dict:
        document_id = document_id['_id']
    elif type(document_id) == list:
        return [delete_document(d) for d in document_id]
    found, document = check_exists(document_id)
    if not found:
        logger.debug('{document_id} does not exist'.format(**locals()))
        return False
    response = client.delete(index=elastic_index, id=document['_id'], doc_type=document['_type'])
    return True

def delete_doctype(doctype):
    '''Delete all documents of a given type'''
    for doc in scroll_query(
        {
        "query":
            {
            "bool":
                {
                "filter":
                    {
                    "term" : {
                        "_type" : doctype
                    }
                    }
                }
            }
        }
    ):
        delete_document(doc['_id'])
    return True

def insert_document(document, custom_identifier=''):
    ''' Insert a new document into the default index '''
    document = _remove_dots(document)
    if not custom_identifier:
        try:
            doc = client.index(index=elastic_index, doc_type=document['_type'], body=document['_source'])
        except ConnectionTimeout:
            doc = {'_id':insert_document(document, custom_identifier)}
    else:
        try:
            doc = client.index(index=elastic_index, doc_type=document['_type'], body=document['_source'], id=custom_identifier)
        except ConnectionTimeout:
            doc= {'_id':insert_document(document['_source'], custom_identifier)}
    logger.debug('added new document, content: {document}'.format(**locals()))
    return doc["_id"]

def insert_documents(documents, identifiers='id'):
    """ Insert a batch of documents in ES

    Parameters
    ----
    documents : list
        a list of document dictionaries to be inserted
    identifiers: string or list
        Specification of the `_id` to assign to the document in elasticsearch.
        Can be either:
            1) A string which specifies which field of the document should be
               used as the id, reverting to ES generated if the id is missing
            2) A list of equal size to the documents, containing the id for
               each document
    Returns
    ----
    List: the ID's under which the documents were inserted

    Note
    ----
    This function assumes that the 'doctype' field is declared in each document
    """
    # preprocess ids
    if type(identifiers) == list:
        logger.debug("Processing identifiers as list")
        if not len(identifiers) == len(documents):
            logger.warning("Identifiers and documents are not of same length, "
            "there are %s docs and %s identifiers!" %(len(documents),len(identifiers))
            )
            raise Exception("Unable to process document batch")
        for doc, identifier in zip(documents, identifiers):
            doc['_id']    = identifier

    if type(identifiers) == str:
        logger.debug("Processing identifiers as key")
        for doc in documents:
            id_value = doc.get(identifiers,"")
            if id_value:
                doc['_id'] = id_value

    for doc in documents:
        doc['_index'] = elastic_index
        doc['_type']  = doc['doctype']
    # Insert documents
    logger.debug(helpers.bulk(client, documents))
    return [doc.get('_id','random') for doc in documents]


def update_or_insert_document(document, force=False, use_url = False):
    ''' Check whether a document exists, update if so
    use_url: if set to True it is additionally checked whether the url already exists. In case either only URL or only id exists the document is not inserted'''
    if '_id' in document.keys():
        exists, _document = check_exists(document['_id'])
        if exists:
            if use_url == True:
                if 'url' in document['_source'].keys():
                    search = client.search(index = elastic_index, body = {'query':{'match':{'url.keyword':document['_source']['url']}}})
                    if search['hits']['total'] != 0:
                        return update_document(document, force=force)
                    else:
                        logger.info("_id found, but no matching URl. Document is not inserted")
            elif use_url == False:
                return update_document(document, force=force)            
        elif not exists:
            if use_url == True:
                try:
                    if 'url' in document['_source'].keys():
                        search = client.search(index = elastic_index, body = {'query':{'match':{'url.keyword':document['_source']['url']}}})
                        if search['hits']['total'] != 0:
                            logger.info("Another document with the same URL already exists in database. Document is not inserted.")
                        else:
                            return insert_document(document)
                except KeyError:
                    logger.info('No URL found, skipping')
            elif use_url == False:
                return insert_document(document,custom_identifier=document['_id'])
    else:
        if use_url == False:
            return insert_document(document)
        elif use_url == True:
            logger.critical('This document has no ID, but you want to check its existence based on the URL. This is not implemented yet, will not insert document')
                        


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
    """Scroll through the results of a query

    Parameters
    ----
    query : dict
        An elasticsearch query
    scroll_time : string (default='10m')
        A string indicating the time-window to keep the results
        buffer active in elasticsearch. A small window risks timeouts, a high
        window risks running into resource ceilings in the database.
    log_interval : int or float
        The interval to log an 'INFO'-level update of progress, defaults to
        argmin (N_results/1000 ; 100). Set to '0' for no logging, a integer for
        every Nth-results and a float for every Nth-fraction of the total

    yields
    ----
    dict
        A stored document, including elasticsearch metadata

    """
    if log_interval == 0:
        total = 0
        update_step =  -1
    else:
        total = client.search(body=query)['hits']['total']
        if type(log_interval)==int:
            update_step = log_interval
        elif type(log_interval)==float:
            update_step = int(total*log_interval)
        else:
            update_step = min((total/1000), 100)

    for n, doc in enumerate(helpers.scan(client, query=query, scroll=scroll_time)):
        if not (n+1 ) % update_step:
            perc = ((n+1)/total) / 100
            logger.info("At item {n:10d} of {total} items | {perc:06.2f}".format(n=n+1, total=total, perc=perc))
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

def id2filename(id):
    """create a filenmame for exporting docments.

    In principle, documents should be saved as {id}.json. However, as ids can 
    be arbitrary strings, filenames can (a) be too long or (b) contain illegal 
    characters like '/'. This function takes care of this
    """
    
    encoded_filename = quote_plus(id)  # use URL encoding to get rid of illegal chacters

    if len(encoded_filename)>132:
        # many filenames allow a maximum of 255 bytes as file name. However, on
        # encrypted file systems, this can be much lower. Therefore, we play safe
        hashed_filename = md5(encoded_filename.encode('utf-8')).hexdigest()
        return encoded_filename[:100]+hashed_filename
    else:
        return encoded_filename

        
    
def export_doctype(doctype):
    if not 'exports' in os.listdir('.'):
        os.mkdir('exports')
    for doc in scroll_query({'query':{'match':{'_type':doctype}}}):
        outpath = os.path.join('exports',quote_plus(doctype))
        if quote_plus(doctype) not in os.listdir('exports'):
            os.mkdir(outpath)
        with open(os.path.join('exports', quote_plus(doctype), '%s.json' %id2filename(doc['_id'])),'w') as f:
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

def import_documents(source_folder, force=False, use_url = False):
    '''use_url: if set to True it is additionally checked whether the url already exists. In case either only URL or only id exists the document is not inserted'''

    for input_file in os.listdir(source_folder):
        doc = json.load(open(os.path.join(source_folder, input_file)))
        update_or_insert_document(doc, force=force, use_url = use_url)
