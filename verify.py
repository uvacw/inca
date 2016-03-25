#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import pymongo
from pymongo import MongoClient
from io import open
import json
from pymongo import MongoClient
import re, sys, unicodedata
import configparser
from collections import defaultdict, OrderedDict
import os



# read config file and set up MongoDB                                           

config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/config.conf')
databasename = config.get('mongodb', 'databasename')
collectionname = config.get('mongodb', 'collectionname')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = MongoClient(config.get('mongodb', 'url'))
db = client[databasename]

collection = db[collectionname]


output=[]
output_irrelevant=[]


#Define searchstring here!
searchstring="ING"


allarticles = collection.find({'$text':{'$search':searchstring}}).batch_size(30)  

for art in allarticles:
    a=0
    reststring =art['text']
    numberofmatches=len(re.findall(searchstring,art['text']))
    poscount=0
    for i in range(numberofmatches):
        print(i)
        print(art['title'])
        try:
            print(art['teaser'])
        except:
            print("geen teaser")
        r=re.search(searchstring,reststring)
        print(poscount)
        if i==0:
            offset=150
            if poscount+r.start() < offset:
                offset=poscount
                print(art['text'][poscount:poscount+r.end()+150])
                answer=input("Is this relevant?")
                if answer in ["yes","Yes","y","Y"]:
                    print("Dit artikel gaat over "+searchstring)
                    k = collection.update({'_id':art['_id']},{"$set": {'project_stockrates':True}})
                    print (k)
                    output.append(art['text'])
                    print(output)
                else:
                    print("Artikel gaat niet over "+searchstring)
                    output_irrelevant.append(art['text'])
            else:
                print(art['text'][poscount+r.start()-offset:poscount+r.end()+150])
                answer=input("Is this relevant?")
                if answer in ["yes","Yes","y","Y"]:
                    print("Dit artikel gaat over "+searchstring)
                    k = collection.update({'_id':art['_id']},{"$set": {'project_stockrates':True}})
                    print (k)
                    output.append(art['text'])
                else:
                    print("Artikel gaat niet over "+searchstring)
                    output_irrelevant.append(art['text'])
        else:
            if art['text'] not in output:
                print(art['text'][poscount+r.start()-150:poscount+r.end()+150])
                answer=input("Is this relevant?")
                if answer in ["yes","Yes","y","Y"]:
                    if art['text'] not in output:
                        print("Dit artikel gaat toch over "+searchstring)
                        k = collection.update({'_id':art['_id']},{"$set": {'project_stockrates':True}})
                        print (k)
                else:
                    print("Artikel gaat niet over "+searchstring)
                    if art['text'] not in output_irrelevant:
                        output_irrelevant.append(art['text'])
            else:
                print("Dit artikel heeft al een key")
        reststring=reststring[r.end():]
        poscount+=r.end()

print(output_irrelevant)


