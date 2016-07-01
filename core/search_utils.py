'''
This file provides basic search functionality for the INCA database. 

'''
from core.database import client

def doctype_first(doctype):
    doc = client.search(index="inca",
                  body={
                      "sort": [
                          {"Publicatiedatum" : {"order":"desc"}}
                          ],
                      "query":
                      {"match":
                       {"doctype":
                        doctype
                       }
                      }}).get('hits',{}).get('hits',[""])[0]
    return doc

def doctype_last(doctype):
    doc = client.search(index="inca",
                  body={
                      "sort": [
                          {"Publicatiedatum" : {"order":"asc"}}
                          ],
                      "query":
                      {"match":
                       {"doctype":
                        doctype
                       }
                      }}).get('hits',{}).get('hits',[""])[0]
    return doc

def doctype_example(doctype):
    return doc

def doctype_fields(doctype):
    '''
    returns a summary of fields for documents of `doctype`:
    field : type - count (coverage)

    note: 
        As elasticsearch does not natively support an 'all fields' query,
        this function runs a 1000 document sample and takes the union of
        found keys as a proxy of fields shared by all documents. 
    '''
    return summary

def doctype_inspect(doctype):
    return summary

