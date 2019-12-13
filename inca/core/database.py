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
from tqdm import tqdm
from hashlib import md5
from .filenames import id2filename

config = configparser.ConfigParser()
config.read('settings.cfg')

logger = logging.getLogger("INCA")
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

try:
    client = Elasticsearch(
        host=config.get('elasticsearch','%s.host' %config.get('inca','dependencies')),
        port=int(config.get('elasticsearch','%s.port'%config.get('inca','dependencies') )),
        scheme=config.get('elasticsearch','%s.scheme' %config.get('inca','dependencies')),
        http_auth=config.get('elasticsearch','%s.http_auth' %config.get('inca','dependencies')),        
        timeout=60
        )
    elastic_index  = config.get("elasticsearch","document_index")
    DATABASE_AVAILABLE = True
    check = int(client.info()['version']['number'][0])
    if check < 6:
        logger.warning("Your version of ElasticSearch is not compatible with inca, version 6 or higher is required. More information can be found here: ... Continuing without database. This means you will not be able to SAVE the results of any scraper or processor!")
        DATABASE_AVAILABLE = False
    # initialize mappings if index does not yet exist
    try:
        #if not elastic_index in client.indices.get_aliases().keys():
        if not client.indices.exists(elastic_index):
            client.indices.create(elastic_index, json.load(open('schema.json')))
    except Exception as e:
        raise Exception("Unable to communicate with elasticsearch, {}".format(e))
except Exception as e:
    logger.warning(e)
    logger.warning("No database functionality available. This means you will not be able to SAVE the results of any scraper or processor!")
    DATABASE_AVAILABLE = False

def get_document(doc_id):
    if not check_exists(doc_id)[0]:
        logger.debug("No document found with id {doc_id}".format(**locals()))
        return {}
    else:
        document = client.get(elastic_index, doc_type='doc', id = doc_id)
    return document

def check_exists(document_id):
    if not DATABASE_AVAILABLE: return False, {}
    if document_id is None or document_id.strip()=='':
        logger.warning('You did not provide a document_id, returning False')
        return False, {}
    index = elastic_index
    try:
        retrieved = client.get(elastic_index,doc_type='doc', id=document_id)
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
    Documents should usually only be appended, not updated as such.

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
                      doc_type='doc',
                      id=document['_id'],
                      body={'doc':document['_source']}
        )
    elif exists and force:
        client.delete(index=elastic_index,
                      doc_type='doc',
                      id=old_document['_id'])
        
        logging.info('FORCED UPDATE of {old_document[_id]}'.format(**locals()))
        document = _remove_dots(document)
        try:
            client.index(index=elastic_index,
                         doc_type='doc',
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
    response = client.delete(index=elastic_index, id=document['_id'], doc_type='doc')
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
                        "doctype" : doctype
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
    
    #Determine document type for Elasticsearch
    #if no document type was found, emit warning and process as "unknown"
    try:
        document_type = document.get('_source',{}).get("doctype",False)
    except KeyError:
        logger.warning("Document without type supplied for indexing in ES!")
        document_type = "unknown"
        document['_source']['doctype'] = document_type
    if not custom_identifier:
        try:
            doc = client.index(index=elastic_index, doc_type='doc', body=document.get('_source',document))
        except ConnectionTimeout:
            doc = {'_id':insert_document(document, custom_identifier)}
    else:
        test = check_exists(custom_identifier)
        if test[0] == True:
            logger.warning("Custom Identifier already exists in database, document is not inserted. Please choose a different identifier.")
            return {}
        else:
            try:
                doc = client.index(index=elastic_index, doc_type='doc', body=document.get('_source',document), id=custom_identifier)
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
            test = check_exists(identifier)
            if test[0] == True:
                logger.warning("Identifier %s already exists in database, document is not inserted. Please choose a different identifier."% identifier)
                identifier = {}
                doc['_id']    = identifier
            else:
                doc['_id']    = identifier

    if type(identifiers) == str:
        logger.debug("Processing identifiers as key")
        for doc in documents:
            id_value = doc.get(identifiers,"")
            if id_value:
                test = check_exists(id_value)
                if test[0] == True:
                    logger.warning("Identifier %s already exists in database, document is not inserted. Please choose a different identifier."% id_value)
                    id_value = {}
                    doc['_id'] = id_value
                else:
                    doc['_id'] = id_value
            else:
                logger.warning("Key for identifier not found, reverting to ES generated.")
                
    documents = [doc for doc in documents if doc['_id'] != {}]
    for doc in documents:
        doc['_index'] = elastic_index
        doc['_type']  = 'doc'
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
                    search = client.search(index = elastic_index, body = {'query':{'term':{'url':document['_source']['url']}}})
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
                        search = client.search(index = elastic_index, body = {'query':{'term':{'url':document['_source']['url']}}})
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
    if you're not careful, it may choke!
    '''
    for k,v in document.items():
        if '.' in k:
            document[k.replace('.','_')]=document.pop(k)
        if type(v)==dict:
            document[k.replace('.','_')]= _remove_dots(v)
    return document

def scroll_query(query,scroll_time='30m', log_interval=None):
    """Scroll through the results of a query

    Parameters
    ----
    query : dict
        An elasticsearch query
    scroll_time : string (default='30m')
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
        total = client.search(index = elastic_index, body=query)['hits']['total']
        if type(log_interval)==int:
            update_step = log_interval
        elif type(log_interval)==float:
            update_step = int(total*log_interval)
        else:
            update_step = min((total/1000), 100)

    for doc in tqdm(helpers.scan(client, index = elastic_index, query=query, scroll=scroll_time), total = total):
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
    path or, alternatively, in the /etc/elasticsearch path. Elasticsearch must be restarted 
    after the `path.repo` is set or changed. In case you are having trouble with 
    starting elasticsearch again, run 
    
    ```bash
    sudo chown elasticsearch.elasticsearch /path/to/inca/backup
    ```
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


def delete_backup(snapshot=None, dryrun=True):
    if snapshot is None:
        print('You need to specify the name of a snapshot to delete. You can get a list of snapshots with .list_backups()')
        return
    command = 'http://%s:%s/_snapshot/inca_backup/%s' %(config.get('elasticsearch','%s.host' %config.get('inca','dependencies')),
                                                  config.get('elasticsearch','%s.port' %config.get('inca','dependencies')),
                                                  snapshot)
    if dryrun==True:
        print('This is a dry-run, nothing happens. If you specify dryrun=False, the following DELETE request will be issued:')
        print(command)
        return
    else:
        response = requests.delete(command)
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
        A string specifying a designation for the snapshot. Useful
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
    if name in [item['snapshot'] for item in list_backups()['snapshots']]:
        client.indices.close('inca')
        client.snapshot.restore(repository='inca_backup', snapshot=name)




#################
# deduplication
################

def deduplicate(g, dryrun=True, check_keys = ["text", "title", "doctype", "publication_date"]):
    '''
    Takes a document generator `g` as input and lists (if `dryrun=True`)
    or remove (if `dryrun=False`) duplicate documents. 
    With ```check_keys = ['key1', 'key2', ...] ``` you can specify the keys
    on which the documents are compared.

    Example usage:
    ```
    g = myinca.database.doctype_generator('nu')
    myinca.database.deduplicate('nu', dryrun = True)
    ```

    Functionality inspired by https://www.elastic.co/blog/how-to-find-and-remove-duplicate-documents-in-elasticsearch
    '''


    dict_of_duplicate_docs = {}
    for doc in g:
        combined_key = ""
        for mykey in check_keys:
            combined_key += str(doc['_source'].get(mykey,''))
        _id = doc["_id"]
        hashval = md5(combined_key.encode('utf-8')).digest()
        dict_of_duplicate_docs.setdefault(hashval, []).append(_id)
    logger.info('Created hashtable')    
        # Search through the hash of doc values to see if any
        # duplicate hashes have been found
    numdups = 0
    if dryrun:
        for hashval, array_of_ids in dict_of_duplicate_docs.items():
            id_to_keep = array_of_ids.pop(0) # let's always keep the first doc
            if len(array_of_ids) > 0:
                # print("********** Duplicate docs hash=%s **********" % hashval)
                # Get the documents that have mapped to the current hashval
                matching_docs = client.mget(index=elastic_index, doc_type='doc',  body={"ids": array_of_ids})
     
                for doc in matching_docs['docs']:
                    numdups +=1
                    try: 
                        print("{}\t{}\t{}".format(
                            doc['_source'].get('title',' '*20)[:20],
                            doc['_source'].get('text',' '*20)[:20],
                            doc['_source'].get('publication_date',' '*10)))
                    except:
                        pass
        print('\nUse a fresh generator and run again with `dryrun=False` to remove these {} documents'.format(numdups))
    else:
        deleted = 0
        to_delete = sum([len(array_of_ids)-1 for array_of_ids in dict_of_duplicate_docs.values()])
        q = 'Type: Yes, go for it! if you really want to delete {} documents '.format(to_delete)
        reallydelete = input(q)
        if reallydelete == 'Yes, go for it!':
            for hashval, array_of_ids in dict_of_duplicate_docs.items():
                id_to_keep = array_of_ids.pop(0) # let's always keep the first doc
                for _id in array_of_ids:
                    try: 
                        client.delete(index=elastic_index,
                                      doc_type='doc',
                                      id=_id)
                        deleted +=1
                    except:
                        print('Could not delete {}.'.format(_id))
            print('Deleted {} documents'.format(deleted))
        



    
######################
# FIX BROKEN DOCUMENTS
######################

def reparse(g, f, force=False):
    '''
    Takes a document generator `g` as reparses the `htmlsource` key using
    a parse function f taken from an INCA-scraper.
  
    In the current implementation, only the text field is considered.
    By default, the text field is only updated if it was empty.

    Arguments
    ---------
    force (bool): If True, non-empty text is replaced as well.

    Example usage:
    ```
    from inca.rssscrapers import news_scraper
    f = news_scraper.nu.parsehtml 
   
    g = myinca.database.document_generator('doctype:"nu" AND publication_date:[2017-01-01 TO 2017-03-15]')
    myinca.database.reparse(g, f, force = False)
    ```
    '''

    # TODO reparse now only repareses the the texts, not other fields (such as author, title etc)
    # To implement that, we need a better logic on which fields are to be replaced when
    
    for doc in g:
        text_old = doc['_source'].get('text', '')
        htmlsource = doc['_source'].get('htmlsource', None)
        if not htmlsource:
            logger.warning('No HTML source')
            continue
        
        _id = doc["_id"]
        if text_old.strip() == '':
            logger.info('No text available for {}, reparsing'.format(_id))
            text_new = f(None, htmlsource)['text'] 
        elif force==True:
            logger.info('Overwriting extisting text for {}, reparsing'.format(_id))
            text_new = f(None,htmlsource)['text'] 
        else:
            logger.debug('Old text exists, will not overwrite')
            continue

        logger.info("Old text: {} characters, first 30: {}".format(
            len(text_old), text_old[:30]))
        logger.info("New text: {} characters, first 30: {}".format(
            len(text_new), text_new[:30]))


        doc['_source']['text'] = text_new
        if len(text_old.strip())>1:
            doc['_source']['text_old'] = text_old   # to be sure, store old text as well

        update_document(doc, force=True) # this force=True has nothing to do with the parameter passed to reparse()
