#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
from pymongo import MongoClient
import re, sys, unicodedata
from os import listdir, walk
from os.path import isfile, join, splitext
import configparser
import argparse
from collections import defaultdict, OrderedDict
import os
import datetime

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
#collectioncleaned = db[collectionnamecleaned]
#collectioncleanedNJR = db[collectionnamecleanedNJR]


VERSIONSTRING="datamanager 0.11"
USERSTRING="damian"



MAAND={"January":1, "januari": 1, "February":2, "februari":2,"March":3,"maart":3,
"April":4, "april":4, "mei":5, "May":5, "June":6,"juni":6, "July":7, "juli":7,
"augustus": 8, "August":8,"september":9,"September":9, "oktober":10,"October":10,
"November":11,"november":11,"December":12,"december":12}

# hier wordt de functie voor het vervangen van leestekens gedefinieerd. Ze worden ERUIT gehaald, niet vervangen door spaties, en dat is juist wat we willen: willem-alexander --> willemalexander
tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))


def remove_punctuation(text):
    return text.replace("`","").replace("´","").translate(tbl)


def insert_lexisnexis(pathwithlnfiles, recursive):
    """
    Usage: insert_lexisnexis(pathwithlnfiles,recursive)
    pathwithlnfiles = path to a directory where lexis nexis output is stored
    recursive: TRUE = search recursively all subdirectories, but include only files ending on .txt
               FALSE = take ALL files from directory supplied, but do not include subdirectories
    """
    tekst = {}
    title ={}
    byline = {}
    section = {}
    length = {}
    loaddate = {}
    language = {}
    pubtype = {}
    journal = {}
    journal2={}
    pubdate_day = {}
    pubdate_month = {}
    pubdate_year = {}
    pubdate_dayofweek = {}

    if recursive:
        alleinputbestanden = []
        for path, subFolders, files in walk(pathwithlnfiles):
            for f in files:
                if isfile(join(path, f)) and splitext(f)[1].lower() == ".txt":
                    alleinputbestanden.append(join(path, f))
    else:
        # print  listdir(pathwithlnfiles)
        alleinputbestanden = [join(pathwithlnfiles, f) for f in listdir(pathwithlnfiles) if
                              isfile(join(pathwithlnfiles, f)) and splitext(f)[1].lower() == ".txt"]
        print(alleinputbestanden)
    artikel = 0
    for bestand in alleinputbestanden:
        print("Now processing", bestand)
        with open(bestand, "r", encoding="utf-8", errors="replace") as f:
            i = 0
            for line in f:
                i = i + 1
                # print "Regel",i,": ", line
                line = line.replace("\r", " ")
                if line == "\n":
                    continue
                matchObj = re.match(r"\s+(\d+) of (\d+) DOCUMENTS", line)
                matchObj2 = re.match(r"\s+(\d{1,2}) (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december) (\d{4}) (maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)", line)
                matchObj3 = re.match(r"\s+(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", line)
                matchObj4 = re.match(r"\s+(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4}) (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", line)
                if matchObj:
                    artikel += 1
                    istitle=True #to make sure that text before mentioning of SECTION is regarded as title, not as body
                    firstdate=True # flag to make sure that only the first time a date is mentioned it is regarded as _the_ date
                    tekst[artikel] = ""
                    title[artikel] = ""
                    while True:
                        nextline=next(f)
                        if nextline.strip()!="":
                            journal2[artikel]=nextline.strip()
                            break
                    continue
                if line.startswith("BYLINE"):
                    byline[artikel] = line.replace("BYLINE: ", "").rstrip("\n")
                elif line.startswith("SECTION"):
                    istitle=False # everything that follows will be main text rather than title if no other keyword is mentioned
                    section[artikel] = line.replace("SECTION: ", "").rstrip("\n")
                elif line.startswith("LENGTH"):
                    length[artikel] = line.replace("LENGTH: ", "").rstrip("\n").rstrip(" woorden")
                elif line.startswith("LOAD-DATE"):
                    loaddate[artikel] = line.replace("LOAD-DATE: ", "").rstrip("\n")
                elif matchObj2 and firstdate==True:
                    # print matchObj2.string
                    pubdate_day[artikel]=matchObj2.group(1)
                    pubdate_month[artikel]=str(MAAND[matchObj2.group(2)])
                    pubdate_year[artikel]=matchObj2.group(3)
                    pubdate_dayofweek[artikel]=matchObj2.group(4)
                    firstdate=False
                elif matchObj3 and firstdate==True:
                    pubdate_day[artikel]=matchObj3.group(2)
                    pubdate_month[artikel]=str(MAAND[matchObj3.group(1)])
                    pubdate_year[artikel]=matchObj3.group(3)
                    pubdate_dayofweek[artikel]="NA"
                    firstdate=False
                elif matchObj4 and firstdate==True:
                    pubdate_day[artikel]=matchObj4.group(1)
                    pubdate_month[artikel]=str(MAAND[matchObj4.group(2)])
                    pubdate_year[artikel]=matchObj4.group(3)
                    pubdate_dayofweek[artikel]=matchObj4.group(4)
                    firstdate=False
                elif (matchObj2 or matchObj3 or matchObj4) and firstdate==False:
                    # if there is a line starting with a date later in the article, treat it as normal text
                    tekst[artikel] = tekst[artikel] + " " + line.rstrip("\n")
                elif line.startswith("LANGUAGE"):
                    language[artikel] = line.replace("LANGUAGE: ", "").rstrip("\n")
                elif line.startswith("PUBLICATION-TYPE"):
                    pubtype[artikel] = line.replace("PUBLICATION-TYPE: ", "").rstrip("\n")
                elif line.startswith("JOURNAL-CODE"):
                    journal[artikel] = line.replace("JOURNAL-CODE: ", "").rstrip("\n")
                elif line.lstrip().startswith("Copyright ") or line.lstrip().startswith("All Rights Reserved"):
                    pass
                elif line.lstrip().startswith("AD/Algemeen Dagblad") or line.lstrip().startswith(
                        "De Telegraaf") or line.lstrip().startswith("Trouw") or line.lstrip().startswith(
                        "de Volkskrant") or line.lstrip().startswith("NRC Handelsblad") or line.lstrip().startswith(
                        "Metro") or line.lstrip().startswith("Spits"):
                    pass
                else:
                    if istitle:
                        title[artikel] = title[artikel] + " " + line.rstrip("\n")
                    else:
                        tekst[artikel] = tekst[artikel] + " " + line.rstrip("\n")
    print("Done!", artikel, "articles added.")

    if not len(journal) == len(journal2) == len(loaddate) == len(section) == len(language) == len(byline) == len(length) == len(tekst) == len(pubdate_year) == len(pubdate_dayofweek) ==len(pubdate_day) ==len(pubdate_month):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Ooooops! Not all articles seem to have data for each field. These are the numbers of fields that where correctly coded (and, of course, they should be equal to the number of articles, which they aren't in all cases.")
        print("journal", len(journal))
        print("journal2", len(journal2))
        print("loaddate", len(loaddate))
        print("pubdate_day",len(pubdate_day))
        print("pubdate_month",len(pubdate_month))
        print("pubdate_year",len(pubdate_year))
        print("pubdate_dayofweek",len(pubdate_dayofweek))
        print("section", len(section))
        print("language", len(language))
        print("byline", len(byline))
        print("length", len(length))
        print("tekst", len(tekst))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!")
        print()
        print("Anyhow, we're gonna proceed and set those invalid fields to 'NA'. However, you should be aware of this when analyzing your data!")


    else:
        print("No missing values encountered.")

    suspicious=0
    for i in range(artikel):
        try:
            art_source = journal[i + 1]
        except:
            art_source = ""
        try:
            art_source2 = journal2[i + 1]
        except:
            art_source2 = ""

        try:
            art_loaddate = loaddate[i + 1]
        except:
            art_loaddate = ""
        try:
            art_pubdate_day = pubdate_day[i + 1]
        except:
            art_pubdate_day = ""
        try:
            art_pubdate_month = pubdate_month[i + 1]
        except:
            art_pubdate_month = ""
        try:
            art_pubdate_year = pubdate_year[i + 1]
        except:
            art_pubdate_year = ""
        try:
            art_pubdate_dayofweek = pubdate_dayofweek[i + 1]
        except:
            art_pubdate_dayofweek = ""
        try:
            art_section = section[i + 1]
        except:
            art_section = ""
        try:
            art_language = language[i + 1]
        except:
            art_language = ""
        try:
            art_length = length[i + 1]
        except:
            art_length = ""
        try:
            art_text = tekst[i + 1]
        except:
            art_text = ""
        try:
            tone=sentiment(art_text)
            art_polarity=str(tone[0])
            art_subjectivity=str(tone[1])
        except:
            art_polarity=""
            art_subjectivity=""
        try:
            art_byline = byline[i + 1]
        except:
            art_byline = ""

        try:
            art_title = title[i + 1]
        except:
            art_title = ""

        # here, we are going to add an extra field for texts that probably are no "real" articles
        # first criterion: stock exchange notacions and similiar lists:
        ii=0
        jj=0
        for token in art_text.replace(",","").replace(".","").split():
            ii+=1
            if token.isdigit():
                jj+=1
        # if more than 16% of the tokens are numbers, then suspicious = True.
        art_suspicious = jj > .16 * ii
        if art_suspicious: suspicious+=1

        art = {
               "title":art_title,
               "source":art_source2.lower(),
               "text":art_text,
               "section":art_section.lower(),
               "byline":art_byline,
               "datum":datetime.datetime(int(art_pubdate_year),int(art_pubdate_month),int(art_pubdate_day)),
               "length_char":len(art_text),
               "length_words":len(art_text.split()),
               "addedby":VERSIONSTRING,
            "addedbydate":datetime.datetime.now(),
            "addedbyuser":USERSTRING
               }

        artnoemptykeys={k: v for k, v in art.items() if v}

        article_id = collection.insert(artnoemptykeys)


    print('\nInserted',len(tekst),"articles, out of which",suspicious,"might not be real articles, but, e.g., lists of stock shares. ")




def adhocclean(bestand):
    repldict = {}
    with open(bestand, "r", encoding="utf-8") as fi:
        for line in fi:
            comline = line.strip().split("\t")
            repldict[comline[0]] = comline[1]
    print("It contains the following rules:")
    print(repldict)
    replpatterns = set(re.compile("\\b" + k + "\\b") for k in repldict)
    allarticles = collectioncleaned.find()
    aantal = collectioncleaned.count()
    i = 0
    numbsub = defaultdict(int)
    for art in allarticles:
        i += 1
        print("\r", i, "/", aantal, " or ", int(i / aantal * 100), "%", end=' ')
        sys.stdout.flush()
        thisart = art["text"]
        doesthisartneedupdate = 0
        for pat in replpatterns:
            subst = pat.subn(repldict[pat.pattern[2:-2]], thisart)  # [2:-2] to strip the \b
            thisart = subst[0]
            numbsub[pat.pattern[2:-2]] += subst[1]
            doesthisartneedupdate += subst[1]
        if doesthisartneedupdate > 0:
            print("Updating article", art["_id"])
            # print collectioncleaned.find({"_id":art["_id"]})[0]
            collectioncleaned.update({"_id": art["_id"]}, {"$set": {"text": thisart}})
    print()
    for k in numbsub:
        print(k, "replaced", numbsub[k], "times")
    print("Done")


def clean_database():


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


    #allarticles = collection.find()
    allarticles = collection.find({"textclean":{ "$exists": False}})
    
    aantal = allarticles.count()
    aantal2 = collection.count()

    print("{}/{} articles have not been cleaned yet and will be cleaned".format(aantal,aantal2))
    i = 0
    for art in allarticles:
        print(art)
        i += 1
        print("\r", i, "/", aantal, " or ", int(i / aantal * 100), "%", end=' ')
        sys.stdout.flush()
        thisart = art["text"].replace("\n", " ")
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

        article_id = collection.update_one({"_id":art["_id"]},{"$set":{"textclean":thisart}})




def clean_database_njr():
    # TODO: is nu copy-paste an gewone functie, beter doen. misschien integreren?

    # initialize new database for cleaned collection
    c = Connection()
    c[databasename].drop_collection(collectionnamecleanedNJR)

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


    allarticles = collection.find()
    aantal = collection.count()
    i = 0
    for art in allarticles:
        i += 1
        print("\r", i, "/", aantal, " or ", int(i / aantal * 100), "%", end=' ')
        sys.stdout.flush()
        thisartorig = art["text"].replace("\n", " ")

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
        # replace original text with  modified text and put the whole item in the cleaned collection
        art["text"] = thisart
        article_id = collectioncleanedNJR.insert(art)


def main():
    parser = argparse.ArgumentParser(
        description="This program is part of VETTE NAAM BEDENKEN PLUS VERWIJZING NAAR ONS PAPER. UITLEG GEVEN HOE HET WERKT.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--overview", help="Give an overview of the data stored in the collection", action="store_true")
    group.add_argument("--overview_cleaned", help="Give an overview of the data stored in the cleaned collection",
                       action="store_true")
    group.add_argument("--overview_cleanednjr", help="Give an overview of the data stored in the cleaned collection of nouns, adjectives, and adverbs",
                       action="store_true")
    group.add_argument("--insert_ln",
                       help="Inserts LexisNexis articles. Name the folder with the input data after --insert_ln", )
    group.add_argument("--clean",
                       help="Creates a cleaned version of your collection by removing punctuation and replacing words as specified in the configuration files.",
                       action="store_true")
    group.add_argument("--cleannjr",
                       help="Creates a cleaned version of your collection by removing punctuation and replacing words as specified in the configuration files, but only keeps nouns, adjectives, and adverbs",
                       action="store_true")
    group.add_argument("--adhocclean",
                       help="Creates a cleaned version of your collection by removing punctuation and replacing words as specified in the configuration files.",
                       nargs=1, metavar="FILE")

    group.add_argument("--delete_all", help="Deletes everything in your database (!!!)", action="store_true")
    parser.add_argument("--recursive", help="Indicates that all subfolders are processed as well", action="store_true")
    # parser.add_argument("folder", help = "The folder in which data to be inserted is stored", nargs="?")

    args = parser.parse_args()

    if args.delete_all:
        print("Do you REALLY want to ERASE the whole collection", collectionname, "within the database", databasename, "?")
        cont = input('Type "Hell, yeah!" and hit Return if you want to continue: ')
        if cont == "Hell, yeah!":
            c = Connection()
            c[databasename].drop_collection(collectionname)
            print("Done. RIP", collectionname)
        else:
            print("OK, you changed your mind. Fine.")

    if args.overview:
        #alles=collection.find()
        #for artikel in alles:
        #       print (artikel["date"],artikel["source"])
        overview1 = collection.aggregate([{"$group": {"_id": "$source", "number": {"$sum": 1}}}])
    
        print(overview1)
        for combi in overview1:
            print(combi["_id"], "\t", combi["number"])


    '''
    if args.overview_cleaned:
        overview1 = collectioncleaned.aggregate([{"$group": {"_id": "$source", "number": {"$sum": 1}}}])
        for combi in overview1["result"]:
            print(combi["_id"], "\t", combi["number"])

    if args.overview_cleanednjr:
        overview1 = collectioncleanedNJR.aggregate([{"$group": {"_id": "$source", "number": {"$sum": 1}}}])
        for combi in overview1["result"]:
            print(combi["_id"], "\t", combi["number"])

    '''

    if args.insert_ln:
        print("Starting to insert", args.insert_ln)
        print("Including subfolders?", args.recursive)
        print("This can take some time...")
        insert_lexisnexis(args.insert_ln, args.recursive)

    if args.clean:
        print("Do you REALLY want to clean the whole collection", collectionname, "within the database", databasename, "right now? This can take VERY long, and you might consider doing this overnight.")
        cont = input('Type "I have time!" and hit Return if you want to continue: ')
        if cont == "I have time!":
            clean_database()
        else:
            print("OK, maybe next time.")

    if args.cleannjr:
        print("Do you REALLY want to clean the whole collection", collectionnamecleanedNJR, "within the database", databasename, "right now? This can take VERY long, and you might consider doing this overnight.")
        cont = input('Type "I have time!" and hit Return if you want to continue: ')
        if cont == "I have time!":
            clean_database_njr()
        else:
            print("OK, maybe next time.")

    if args.adhocclean:
        bestand = args.adhocclean[0]
        print("Re-processing the cleaned database with the instructions provided in", bestand, "\n")
        adhocclean(bestand)


if __name__ == "__main__":
    main()
