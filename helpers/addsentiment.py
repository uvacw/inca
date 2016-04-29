#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pymongo
import configparser
import os
from sentipy import senti, sentifile




# read config file and set up MongoDB
config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/../config.conf')

### JUSR FOR NOW:
databasename='sandbox'
#databasename=config.get('mongodb','databasename')
###

collectionname=config.get('mongodb','collectionname')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = pymongo.MongoClient(config.get('mongodb','url'))
db = client[databasename]
db.authenticate(username,password)
collection = db[collectionname]



docs=collection.find({'project_stockrates':True})

for doc in docs:
    sentiment=(senti(doc['text'],'dutch'))
    positivity=sentiment[0]
    negativity=sentiment[1]
    r = collection.update({'_id':doc['_id']},{"$set": {'positivity':positivity,'negativity':negativity}})
    print (r)
