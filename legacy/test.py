import logging
import json
from elasticsearch import Elasticsearch, NotFoundError, helpers
from elasticsearch.exceptions import ConnectionTimeout
import time
import configparser
import requests
from celery import Task
import os

config = configparser.ConfigParser()
config.read('settings.cfg')

logger = logging.getLogger(__name__)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

client = Elasticsearch(
    host=config.get('elasticsearch','%s.host' %config.get('inca','dependencies')),
    port=int(config.get('elasticsearch','%s.port'%config.get('inca','dependencies') )),
    timeout=60
)   # should be updated to reflect config                                                                                                                                                                   
elastic_index  = config.get("elasticsearch","document_index")

# initialize mappings if index does not yet exist                                                                                                                                                           
try:
    if not elastic_index in client.indices.get_aliases().keys():
        client.indices.create(elastic_index, json.load(open('schema.json')))
except Exception as e:
    raise Exception("Unable to communicate with elasticsearch, {}".format(e))

