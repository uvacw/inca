#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pymongo
import configparser
import os
from datetime import datetime
from sentipy import senti, sentifile




# read config file and set up MongoDB
config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/../config.conf')

### JUSR FOR NOW:
#databasename='sandbox'

databasename=config.get('mongodb','databasename')

collectionname=config.get('mongodb','collectionname')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = pymongo.MongoClient(config.get('mongodb','url'))
db = client[databasename]
db.authenticate(username,password)
collection = db[collectionname]


OVERWRITE=False  # False means that sentiment score is only calculated if not already present

#docs=collection.find({'project_stockrates':True})
docs=collection.find({
    'datum':
    {
   '$gte':datetime(2014,1,1),
   '$lte':datetime(2014,12,31)
  }
}   )


aantal=docs.count()
i=0
for doc in docs:
    i+=1
    if ('positivity' in doc) and (OVERWRITE==False):
        # skip the doc
        continue
    if 'text' in doc:
        sentiment=(senti(doc['text'],'dutch'))
        positivity=sentiment[0]
        negativity=sentiment[1]
        r = collection.update({'_id':doc['_id']},{"$set": {'positivity':positivity,'negativity':negativity}})
    else:
        r='ARTIKEL HEEFT GEEN TEKST, KAN DUS GEEN SENTIMENT BEREKENEN'
    print ('{}/{}\t{}'.format(i,aantal,r))
