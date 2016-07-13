'''
This file provides basic search functionality for the INCA database. 

'''
from core.database import client
import configparser

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))
elastic_index = config.get('elasticsearch','document_index')

def doctypes():
    existing_doctypes = [key for key in client.indices.get_mapping(elastic_index).get(elastic_index,{}).get('mappings',{}).keys() if
                         key != '_default_' and key != 'core.document']
    overview = {doctype:client.search(index=elastic_index,doc_type=doctype).get('hits',{}).get('total',"NA") for
                                                                                        doctype in existing_doctypes}
    return overview

def doctype_first(doctype, num=1):
    docs = client.search(index=elastic_index,
                  body={
                      "sort": [
                          {"Publicatiedatum" : {"order":"desc"}}
                          ],
                      "size":num,
                      "query":
                      {"match":
                       {"doctype":
                        doctype
                       }
                      }}).get('hits',{}).get('hits',[""])
    return docs

def doctype_last(doctype,num=1):
    docs = client.search(index=elastic_index,
                  body={
                      "sort": [
                          {"Publicatiedatum" : {"order":"asc"}}
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
                            "doctype": doctype
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
    doc_num   = 0
    mappings = client.indices.get_mapping(elastic_index).get(elastic_index,{}).get('mappings',{}).get(doctype,{}).get('properties',{})
    for num, doc in enumerate(doctype_examples(doctype, num=1000)):
        doc_num = num+1
        [key_count.update([key]) for key in doc.get('_source',{}).keys()]
    summary = {k:{'coverage':v/doc_num,'type':mappings[k].get('type','unknown')} for k,v in key_count.items()}
    return summary

def doctype_inspect(doctype):

    summary = dict(
        total_collected=0,
        first_collected=datetime(),
        last_collected=datetime(),
        keys=doctype_fields(doctype)
    )
    return summary

def scroll_query(query,scroll_time='2m'):
    scroller = client.search(elastic_index,
                             body=query,
                             scroll=scroll_time,
                             search_type='scan')
    sid  = scroller['_scroll_id']
    size = scroller['hits']['total']
    while size > 0 :
        page = client.scroll(scroll_id = sid,
                             scroll = scroll_time)
        sid = page['_scroll_id']
        size = len(page['hits']['hits'])

        for doc in page['hits']['hits']:
            yield doc
