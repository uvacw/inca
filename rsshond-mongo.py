#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from io import open
import json
from pymongo import MongoClient
import re, sys, unicodedata
import configparser
from collections import defaultdict, OrderedDict
import os


import sys
import re
import feedparser
import os.path
import urllib.request, urllib.error, urllib.parse
import time
import csv
import os
import datetime
import urllib


from urllib import request
from time import sleep
from random import randint
from lxml import html

from nieuwsparsers import *




VERSIONSTRING="rsshond-mongo 0.1"
USERSTRING="damian"


# read config file and set up MongoDB
config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/config.conf')
databasename = config.get('mongodb', 'databasename')
collectionname = config.get('mongodb', 'collectionname')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = MongoClient(config.get('mongodb', 'url'))
db = client[databasename]
db.authenticate(username,password)

collection = db[collectionname]



#stuff for cookie and redirect handling
class MyHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)        
    http_error_301 = http_error_303 = http_error_307 = http_error_302

cookieprocessor = urllib.request.HTTPCookieProcessor()

opener = urllib.request.build_opener(MyHTTPRedirectHandler, cookieprocessor)
urllib.request.install_opener(opener)



def parse (medium, doc, ids, titel):
    '''
    This is a function that calls the right parser
    It returns nothing, but saves the parsed contents to a series of 
    csv-files
    '''

    if medium=="nunl" or medium=="nunieuw":
        print("I just chose the nu parser")
        elements=parse_nu(doc,ids,titel)
    #elif medium=="ad":
        #print("I just chose ad parser.")
        #elements=parse_ad(doc,ids,titel)
    elif medium=="volkskrantnl":
        print("I just chose the VK-parser")
        elements=parse_vk(doc,ids,titel)
    elif medium=="nrcnl":
        print("I just chose nrc parser")
        elements=parse_nrc(doc,ids,titel)
    elif medium=="telegraafnl":
        print("I just chose Tele parser")
        elements=parse_telegraaf(doc,ids,titel)
    elif medium=="spitsnl":
        print("I just chose Spits parser")
        elements=parse_spits(doc,ids,titel)
    elif medium=="metronieuwsnl":
        print("I just chose Metro parser")
        elements=parse_metronieuws(doc,ids,titel)
    elif medium=="trouwnl":
        print("I just chose Trouw parser")
        elements=parse_trouw(doc,ids,titel)
    elif medium=="paroolnl":
        print("I just chose Parool parser")
        elements=parse_parool(doc,ids,titel)
    elif medium=="nosnl":
        print("I just chose NOS parser")
        elements=parse_nos(doc,ids,titel)
    elif medium=="tponl":
        print("I just chose Tpo parser")
        elements=parse_tpo(doc,ids,titel)
    elif medium=="geenstijlnl":
        print("I just chose Geenstijl parser")
        elements=parse_geenstijl(doc,ids,titel)
    elif medium=="sargassonl":
        print("I just chose Sargasso parser")
        elements=parse_sargasso(doc,ids,titel)
    elif medium=="foknl":
        print("I just chose Fok parser")
        elements=parse_fok(doc,ids,titel)
    else:
        print("Er bestaat nog geen parser voor"+medium)
        return

    listelements=list(elements)

    return listelements



#Function that checks feeds defined here
def checkfeeds(waarvandaan, waarnaartoe,sourcename):
    waarnaartoestem=waarnaartoe.split(".")[0]
    d = feedparser.parse(waarvandaan)
    artikel_id=[]
    artikel_datum=[]
    artikel_kop=[]
    artikel_teaser=[]
    artikel_link=[]
    artikel_filename=[]
    
    nieuweposts=0
 
    for post in d.entries:
        i=0
        # sommige feeds (bijvoorbeeld die van joop.nl) laten het identificatieveld leeg, in dat geval gebruiken we de link in plaats van het id-veld
        try:
            identificatie=post.id
        except:
            identificatie=post.link

        # alleen nieuwe posts die we nog niet hebben toevoegen
        if collection.find({"rssidentifier":identificatie},{"_id":1}).count()==0:
            nieuweposts+=1
  
            if waarnaartoestem=="volkskrantnl":
                print(post.link)
                mylink=re.sub("/$","",post.link)
                mylink="http://www.volkskrant.nl//cookiewall/accept?url="+mylink
                req=urllib.request.Request((mylink))          
            elif waarnaartoestem=="adnl":
                mylink=re.sub("/$","",post.link)
                mylink="http://www.ad.nl/ad/acceptCookieCheck.do?url="+mylink
                req=urllib.request.Request((mylink))
            elif waarnaartoestem=="trouwnl":
                mylink=re.sub("/$","",post.link)
                mylink="http://www.trouw.nl/tr/acceptCookieCheck.do?url="+mylink
                req=urllib.request.Request((mylink))
            elif waarnaartoestem=="paroolnl":
                mylink=re.sub("/$","",post.link)
                mylink="http://www.parool.nl/parool/acceptCookieCheck.do?url="+mylink
                req=urllib.request.Request((mylink))
            else: 
                req=urllib.request.Request(re.sub("/$","",post.link), headers={'User-Agent' : "Wget/1.9"})
            
            response = urllib.request.urlopen(req)
            
            title,text,category,byline,bylinesource=parse(waarnaartoestem,response.read().decode(encoding="utf-8",errors="ignore"),identificatie,re.sub(r"\n|\r\|\t"," ",post.title))

            try:
                teaser=re.sub(r"\n|\r\|\t"," ",post.description)
            except:
                teaser=""


            art = {"rssidentifier":identificatie, 
                   "title":post.title,
                   "teaser":teaser,
                   "source":sourcename,
                   "text":text,
                   "section":category,
                   "byline":byline,
                   "bylinesource":bylinesource,
                   "datum":datetime.datetime(*feedparser._parse_date(post.published)[:6]),
                   "length_char":len(text),
                   "length_words":len(text.split()),
                   "addedby":VERSIONSTRING,
                   "addedbyuser":USERSTRING,
                   "addedbydate":datetime.datetime.now(),
                   "url":re.sub("/$","",post.link)}

            artnoemptykeys={k: v for k, v in art.items() if v}

            article_id = collection.insert(artnoemptykeys)


            i=i=1
    if nieuweposts==0:
        print("0 nieuwe artikelen gevonden op "+waarvandaan)
    else:
        print(str(nieuweposts)+"/"+str(len(d.entries)),"nieuwe artikelen gevonden op "+waarvandaan+". "+waarnaartoe+" is bijgewerkt en de artikelen zijn gedownload")



# begin program

if __name__ == "__main__":
    print("\n")
    print("Welkom bij rsshond 0.2 (by Damian Trilling, www.damiantrilling.net)")
    print("Current date & time: " + time.strftime("%c"))
    print("\n")

    with open("sources.conf",mode="r",encoding="utf-8") as csvfile:
        reader=csv.reader(csvfile,delimiter=",")
        for row in reader:
                checkfeeds (row[1],row[0],row[2])
