#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable()
form = cgi.FieldStorage()
from __future__ import unicode_literals
from __future__ import division
from io import open
from pymongo import MongoClient, Connection, TEXT
import argparse
import ConfigParser
from collections import Counter, defaultdict
import sys
from nltk.stem import SnowballStemmer
from itertools import combinations, chain
import ast
from numpy import log
from gensim import corpora, models, similarities
import numpy as np
from sklearn.decomposition import PCA
import os
import coocnet from analysis
import frequencies from analysis

# read config file and set up MongoDB
config = ConfigParser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/config.conf')
dictionaryfile=config.get('files','dictionary')
networkoutputfile=config.get('files','networkoutput')
lloutputfile=config.get('files','loglikelihoodoutput')
lloutputcorp1file=config.get('files','loglikelihoodoutputoverrepcorp1')
cosdistoutputfile=config.get('files','cosdistoutput')
compscoreoutputfile=config.get('files','compscoreoutput')
clusteroutputfile=config.get('files','clusteroutput')
ldaoutputfile=config.get('files','ldaoutput')
databasename=config.get('mongodb','databasename')
collectionname=config.get('mongodb','collectionname')
collectionnamecleaned=config.get('mongodb','collectionnamecleaned')
collectionnamecleanedNJR = config.get('mongodb','collectionnamecleanedNJR')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = MongoClient(config.get('mongodb','url'))
db = client[databasename]
db.authenticate(username,password)
collection = db[collectionname]

if form.getvalue('NRC'):
	nrc_flag = 'NRC'
else:
	nrc_flag = ''
if form.getvalue('De Volkskrant'):
	volkskrant_flag = 'De Volkskrant'
else:
	volkskrant_flag = ''

if form.getvalue('mostpop'):
	topwords = form.getvalue('mostpop')
else:
	topwords = "missing value for top words"

if form.getvalue('maxcooc'):
	maxcooc = form.getvalue('maxcooc')
else:
	maxcooc = "missing value for maximum amount of co-occurences"

def split2ngrams(txt, n):
    if n==1:
        return txt.split()
    else:
        return [tuple(txt.split()[i:i+n]) for i in range(len(txt.split())-(n-1))]

def frequencies():
    '''
    returns a counter object of word frequencies
    '''
    
    all=collectioncleaned.find(subset,{"text": 1, "_id":0})
    aantal=all.count()
    # print all[50]["text"]
    c=Counter()
    i=0
    for item in all:
       i+=1
       print "\r",i,"/",aantal," or ",int(i/aantal*100),"%",
       sys.stdout.flush()
       #c.update([woord for woord in item["text"].split()])
       if stemming==0:
           c.update([woord for woord in split2ngrams(item["text"],ngrams)]) 
       else:
           c.update([woord for woord in split2ngrams(stemmed(item["text"],stemming_language),ngrams)])  
    print
    return c



def coocnet(n,minedgeweight):
    ''' 
    n = top n words
    minedgeweight = minimum number of co-occurances (=edgeweight) to be included
    '''


    '''
    TODO
    
    GIVE THE OPTION TO DETERMINE WHAT HAS TO BE INCLUDED BASED ON LOGLIKELIHOOD ETC INSTEAD OF RAW FREQUENCIES
    '''

    #  place file somewhere where it can be downladed
    networkoutputfile="/var/www/html/networkoutput.csv"
    
    cooc=defaultdict(int)
    
    print "Determining the",n,"most frequent words...\n"
    c=frequencies()
    topnwords=set([a for a,b in c.most_common(n)])
    #debug, volgende regel later weer weghalen
    print topnwords
    all=collectioncleaned.find(subset,{"text": 1, "_id":0})
    aantal=all.count()
    
    print "\n\nDetermining the cooccurrances of these words with a minimum cooccurance of",minedgeweight,"...\n"
    i=0
    for item in all:
        i+=1
        print "\r",i,"/",aantal," or ",int(i/aantal*100),"%",
        #words=item["text"].split()

        if stemming==0:
            words=split2ngrams(item["text"],ngrams)
        else:
            words=split2ngrams(stemmed(item["text"],stemming_language),ngrams)

        wordsfilterd=[w for w in words if w in topnwords]        
        uniquecombi = set(combinations(wordsfilterd,2))
        for a,b in uniquecombi:
            if (b,a) in cooc:
                a, b = b,a
            if a!=b:
                cooc[(a,b)]+=1


    with open(networkoutputfile,mode="w",encoding="utf-8") as f:
        f.write("nodedef>name VARCHAR, width DOUBLE\n")
        algenoemd=[]
        verwijderen=[]
        for k in cooc:
                if cooc[k]<minedgeweight:
                        verwijderen.append(k)
                else:
                        if k[0] not in algenoemd:
                                #f.write(k[0]+","+str(c[k[0]])+"\n")
                                f.write(unicode(k[0])+","+unicode(c[k[0]])+"\n")
                                algenoemd.append(k[0])
                        if k[1] not in algenoemd:
                                #f.write(k[1]+","+str(c[k[1]])+"\n")
                                f.write(unicode(k[1])+","+unicode(c[k[1]])+"\n")
                                algenoemd.append(k[1])
        for k in verwijderen:
                del cooc[k]

        f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
        for k, v in cooc.iteritems():
                # next line is necessary for the case of ngrams (we want the INNER TUPLES (the ngrams) become strings
                k2=[unicode(partofngram) for partofngram in k]
                regel= ",".join(k2)+","+str(v)
                f.write(regel+"\n")

    print "\nDone. Network file written to",networkoutputfile

  
print('Content-Type: text/html')
print('''

<html>
<head>
<title>This is the demo newspaper choice Program</title>
</head>
<body>
<h2>We are currently running an analysis on the top %s most common words from the following newspapers:</h2> </br>
<h3>%s<br>%s</h3>
<h6> <a href='wordcount.py' target='blank'> Click here to retrieve the most common words alone </a></h6> 
<h3>Out of those, we will retrieve the top %s co-occurences between them</h3>
''' % (topwords,nrc_flag,volkskrant_flag,maxcooc))

coocnet(topwords,maxcooc)

#TODO: make sure that the user does not get the link before the analysis is finished...

print('''
You can download the file <a href=whateverfilename.csv>here</a>

</body>
</html>
''')
