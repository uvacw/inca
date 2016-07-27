'''
This file provides basic search functionality for the INCA database.
'''
from core.database import client, scroll_query
import configparser
import logging

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))
elastic_index = config.get('elasticsearch','document_index')

def doctypes():
    existing_doctypes = [key for key in client.indices.get_mapping(elastic_index).get(elastic_index,{}).get('mappings',{}).keys() if
                         key != '_default_' and key != 'core.document']
    overview = {doctype:client.search(index=elastic_index,doc_type=doctype).get('hits',{}).get('total',"NA") for
                                                                                        doctype in existing_doctypes}
    return overview

def doctype_generator(doctype):
    query = {'filter':{'match':{'doctype':doctype}}}
    for num, doc in enumerate(scroll_query(query)):
        logger.info("returning {num}".format(**locals()))
        yield doc

def doctype_first(doctype, num=1, by_field=""):
    '''Returns the first document of a given doctype

    Input
    ---
    doctype: string
        The document type you whish to retrieved
    num: int
        The number of documents to retrieve
    by_field: string
        The datetime field by which to determine the
        first document 
    '''
    docs = client.search(index=elastic_index,
                  body={
                      "sort": [
                          {by_field : {"order":"desc"}}
                          ],
                      "size":num,
                      "query":
                      {"match":
                       {"doctype":
                        doctype
                       }
                      }}).get('hits',{}).get('hits',[""])
    return docs

def doctype_last(doctype,num=1, by_field=""):
    '''Returns the last document of a given doctype

    Input
    ---
    doctype: string
        The document type you whish to retrieved
    num: int
        The number of documents to retrieve
    by_field: string
        The datetime field by which to determine the
        last document 
    '''
    docs = client.search(index=elastic_index,
                  body={
                      "sort": [
                          { by_field : {"order":"asc"}}
                          ],
                      "size":num,
                      "query":
                      {"match":
                       {"doctype":
                        doctype
                       }
                      }}).get('hits',{}).get('hits',[""])
    return docs

def doctype_examples(doctype, seed=42, num=10):
    docs = client.search(index=elastic_index, body={
        'size':num,
        "query": {
            "function_score": {
                "filter": {
                       
                        "match": {
                            "_type": doctype
                            }
                 
                    },
                "functions": [
                    {
                        "random_score": {
                            "seed": seed
                            }
                        }
                    ]
                }}
    })
    return docs['hits']['hits']

def doctype_fields(doctype):
    '''
    returns a summary of fields for documents of `doctype`:
    field : type - count (coverage)

    note: 
        As elasticsearch does not natively support an 'all fields' query,
        this function runs a 1000 document sample and takes the union of
        found keys as a proxy of fields shared by all documents. 
    '''
    from collections import Counter
    key_count = Counter()
    doc_num   = client.search(index=elastic_index, body={'query':{'match':{'_type':doctype}}})['hits']['total']
    mappings = client.indices.get_mapping(elastic_index).get(elastic_index,{}).get('mappings',{}).get(doctype,{}).get('properties',{})
    coverage = {key:client.search(elastic_index,body={'query':{'exists':{'field':key}},
                                                      'filter':{'match':{'doctype':doctype}}}).get('hits',{}).get('total',0) for key in mappings.keys()}

    #for num, doc in enumerate(doctype_examples(doctype, num=1000)):
    #    doc_num = num+1
    #    [key_count.update([key]) for key in doc.get('_source',{}).keys()]
    summary = {k:{'coverage':coverage.get(k,'unknown')/float(doc_num),'type':mappings[k].get('type','unknown')} for k in mappings.keys()}
    return summary

def doctype_inspect(doctype):
    '''TODO: provide an overview of doctype collection '''
    summary = dict(
        total_collected=0,
        first_collected=datetime(),
        last_collected=datetime(),
        keys=doctype_fields(doctype)
    )
    return summary

