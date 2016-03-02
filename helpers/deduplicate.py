#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pymongo import MongoClient
import configparser
from datetime import datetime,timedelta
import os

# read config file and set up MongoDB
config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/../config.conf')
databasename = config.get('mongodb', 'databasename')
collectionname = config.get('mongodb', 'collectionname')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = MongoClient(config.get('mongodb', 'url'))
db = client[databasename]
db.authenticate(username,password)

collection = db[collectionname]

global INTERVAL
INTERVAL=1 # set to 1 means that duplicates are only duplicates i they appear on the same day


def gendatetuples(start,end):
    '''
    yields tuples of dates for using in repeated queries
    '''
    d = start
    while d <= end:
        yield d, d + timedelta(days=INTERVAL)
        d += timedelta(days=INTERVAL)



def createdupfile(source,start,end):
    output=[]
    for datetuple in gendatetuples(start,end):
        # duplicates are defined as texts that appear EXACTLY twice, if we want to include
        # thinks that occur more often, the count: 2 has to be modified
        myquery = [{'$match': {'$and':[
            {'source':source},
            {'datum':  {
                '$gte':datetuple[0],
                '$lt':datetuple[1]}}]}},
            {'$group':{'_id':'$text', 'count':{'$sum':1}}}, {'$match': {'count':2}} ]
        
        c=collection.aggregate(myquery)
        for e in c:
            output.append(e)
    with open('../output/'+source+'.json',mode='w',encoding='utf-8') as fo:
        json.dump(output,fo)



tasks=[('nrc (print)',datetime(1990,1,1),datetime(2016,1,1)),('volkskrant (print)',datetime(1990,1,1),datetime(2016,1,1))]

for task in tasks:
    print('Processing {} {} {}'.format(task[0],task[1],task[2]))
    createdupfile(task[0],task[1],task[2])

#x=gendatetuples(datetime(2013,1,1),datetime(2013,1,20))
#for e in x:
#    print(e)
