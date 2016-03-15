#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division

import json
from pymongo import MongoClient
import re, sys, unicodedata
import configparser
import argparse
from collections import defaultdict, OrderedDict
import os
import datetime
import ast
from io import open

# TODO
# variabele toon toevoegen

# read config file and set up MongoDB
config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/config.conf')
replacementlistfile = config.get('files', 'replacementlist')
stopwordsfile = config.get('files', 'stopwords')
replacementlistlastnamesfile = config.get('files', 'replacementlistlastnames')
replacementlistsindienfile = config.get('files', 'replacementlistotherindicator')
databasename = config.get('mongodb', 'databasename')
collectionname = config.get('mongodb', 'collectionname')


# DIT WORDT DUS ANDERS
# TODO NEW FIELD INSTEAD OF NEW COLLECTION
#collectionnamecleaned = config.get('mongodb', 'collectionnamecleaned')
#collectionnamecleanedNJR = config.get('mongodb','collectionnamecleanedNJR')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = MongoClient(config.get('mongodb', 'url'))
db = client[databasename]
#db.authenticate(username,password)

collection = db[collectionname]








# hier wordt de functie voor het vervangen van leestekens gedefinieerd. Ze worden ERUIT gehaald, niet vervangen door spaties, en dat is juist wat we willen: willem-alexander --> willemalexander
tbl = dict.fromkeys(i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P'))

def remove_punctuation(text):
    return text.replace("`","").replace("´","").replace("|"," ").translate(tbl)




def clean_database_njr():


    # load replacement lists
    # replacement list 1: always replace
    with open(replacementlistfile, mode="r", encoding="utf-8") as fi:
        repldict = json.load(fi, object_pairs_hook=OrderedDict)
    replpatterns = set(re.compile("\\b" + k + "\\b") for k in repldict)
    # replacement list 2: replace if already replaced according to list 1
    with open(replacementlistlastnamesfile, mode="r", encoding="utf-8") as fi:
        repldictpersons = json.load(fi, object_pairs_hook=OrderedDict)
    # replacement list 3: replace only if another expression is mentioned
    with open(replacementlistsindienfile, mode="r", encoding="utf-8") as fi:
        repldictindien = json.load(fi, object_pairs_hook=OrderedDict)


    allarticles = collection.find(subset)
    aantal = collection.find(subset).count()
    i = 0
    for art in allarticles:
        i += 1
        print "\r", i, "/", aantal, " or ", int(i / aantal * 100), "%",
        sys.stdout.flush()
        try:
            thisartorig = art["text"].replace("\n", " ")
        except:
            # do nothing with this article if it does not have any text
            print
            print 'Weird, this article did not have any text body, skipping it'
            print
            continue

        # hier is t dus interessant

        from pattern.nl import parse
        thisart=""
        for zin in parse(thisartorig).split():
                for token in zin:
                    if token[1].startswith('N') or token[1].startswith('J') or token[1].startswith('R'):
                        #print token[0],token[1]
                        thisart+=(" "+token[0])
        #print thisart


        numbsub = 0
        for pat in replpatterns:
            subst = pat.subn(repldict[pat.pattern[2:-2]], thisart)  #[2:-2] to strip the \b
            thisart = subst[0]
            numbsub += subst[1]
        # only if sth has been substituted at all, check if it's a last name that has to be substituted as well
        # functie 1b: als iemand een keer met z'n volledige naam genoemd wordt, ook de volgende keren dat alleen z'n achternaam wordt genoemd deze vervangen
        if numbsub > 0:
            for k, v in repldictpersons.items():
                #print "For",k,", there are",len(v),"rules."
                for vv in v:
                    if vv in thisart:
                        thisart = re.sub("\\b" + k + "\\b", vv, thisart)
                        #print "Replaced",k,"by",vv
        for k, v in repldictindien.items():
            if re.findall("\\b" + k + "\\b",thisart):
                for vv in v:
                    #print "checking vv",vv,"and k",k
                    thisart = re.sub("\\b" + vv[0] + "\\b", vv[1], thisart)
                #print "Replaced", vv[0], "by", vv[1], "because", k, "was mentioned"


        thisart = remove_punctuation(thisart.lower())
        stops = [line.strip().lower() for line in open(stopwordsfile, mode="r", encoding="utf-8")]
        tas = thisart.split()
        thisart = ""
        for woord in tas:
            if (woord not in stops) and (not woord.isdigit()):
                thisart = " ".join([thisart, woord])

        r = collection.update({'_id':art['_id']},{"$set": {'textclean_njr':thisart}})
        print r


def main():
    parser = argparse.ArgumentParser(
        description="This program is part of VETTE NAAM BEDENKEN PLUS VERWIJZING NAAR ONS PAPER. UITLEG GEVEN HOE HET WERKT.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cleannjr",
                       help="Creates a cleaned version of your collection by removing punctuation and replacing words as specified in the configuration files, but only keeps nouns, adjectives, and adverbs",
                       action="store_true")
    parser.add_argument("--subset", help="Use MongoDB-style .find() filter in form of a Python dict. E.g.:  --subset=\"{'source':'de Volkskrant'}\" or --subset=\"{'\\$text':{'\\$search':'hema'}\"or a combination of both: --subset=\"{'\\$text':{'\\$search':'hema'}}\",'source':'de Volkskrant'}\"")


    args = parser.parse_args()

    global subset
    if not args.subset:
        subset={}
    else:
        try:
            subset=ast.literal_eval(args.subset)
        except:
            print("You specified an invalid filter!")
            sys.exit()

        if type(subset) is not dict:
            print("You specified an invalid filter!")
            sys.exit()

        print("Task will only be performed on the subset ",subset)



    if args.cleannjr:
        print "Do you REALLY want to start right now? This can take VERY long, and you might consider doing this overnight."
        cont = raw_input('Type "I have time!" and hit Return if you want to continue: ')
        if cont == "I have time!":
            clean_database_njr()
        else:
            print("OK, maybe next time.")



if __name__ == "__main__":
    main()
