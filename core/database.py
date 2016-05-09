'''

This module provides database access objects.

TODO: factor in settings 

'''


import logging
import pymongo

logger = logging.getLogger(__name__)

client = pymongo.MongoClient()

document_collection = client.inca.documents

user_collection     = client.inca.users
