#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import open
from collections import OrderedDict
import json
import ConfigParser
import sys
import os

config = ConfigParser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/../config.conf')

nlwoordenbestand=config.get('files','dictionary')

ownreplacements=[config.get('files','ownreplacements')] 


outputbestand=config.get('files','replacementlist')
outputbestand2=config.get('files','replacementlistlastnames')
outputbestand3=config.get('files','replacementlistotherindicator')



def replacespaces(listwithwords):
    repldict={}
    wordswithspace=[woord for woord in listwithwords if woord.find(" ")>-1]
    print len(wordswithspace),"expressions containing spaces (from the dictionary) have been added to the replacement list"
    for woord in wordswithspace:
        repldict[woord]=woord.replace(" ","_")
    return repldict
    


def replaceown(inputfiles,col1,col2):
    '''
    col1 = column with the original expression
    col2 = column with the replacement
    '''
    repldict=OrderedDict()
    for fname in inputfiles:
        i=0
        with open(fname,mode="r",encoding="utf-8") as fi:
            for line in fi:
                i+=1
                #print "\r",fname,": line",i,
                #sys.stdout.flush()
                bothcolumns=line.strip().split("\t")
                #print bothcolumns
                # alleen doorgaan als de kolom bestaat
                if len(bothcolumns)-1>=max(col1,col2):
                    repldict[bothcolumns[col1]]=bothcolumns[col2]
        #print "\n",i,"expressions from",fname,"have been added to the replacement list"
    return repldict




def replaceownlistoutput(inputfiles,col1,col2):
    '''
    col1 = column with the original expression
    col2 = column with the replacement
    '''
    repldict=OrderedDict()
    for fname in inputfiles:
        i=0
        with open(fname,mode="r",encoding="utf-8") as fi:
            for line in fi:
                i+=1
                #print "\r",fname,": line",i,
                #sys.stdout.flush()
                bothcolumns=line.strip().split("\t")
                #print bothcolumns
                # alleen doorgaan als de kolom bestaat
                if len(bothcolumns)-1>=max(col1,col2):
                    if bothcolumns[col1] in repldict:
                        #print "key:",bothcolumns[col1],"already exists with value",repldict[bothcolumns[col1]]
                        #print "Skipping the following combination:"
                        #print "Appending"
                        #print "key:",bothcolumns[col1],"value:",bothcolumns[col2]
                        repldict[bothcolumns[col1]]+=[bothcolumns[col2]]
                    else:
                        repldict[bothcolumns[col1]]=[bothcolumns[col2]]
                    #print bothcolumns[col1],bothcolumns[col2]
        #print "\n",i,"expressions from",fname,"have been added to the replacement list"
    return repldict

    
def replaceownindien(inputfiles,col1,col2,col3):
    '''
    col1 = column with the original expression
    col2 = column with the replacement
    col3= indien DIT genoemd wordt in het artikel
    '''
    repldict=OrderedDict()
    for fname in inputfiles:
        i=0
        with open(fname,mode="r",encoding="utf-8") as fi:
            for line in fi:
                i+=1
                #print "\r",fname,": line",i,
                #sys.stdout.flush()
                bothcolumns=line.strip().split("\t")
                #print bothcolumns
                # alleen doorgaan als de kolom bestaat
                if len(bothcolumns)-1>max(col1,col2):
                    if bothcolumns[col3] in repldict:
                        repldict[bothcolumns[col3]]+=[[bothcolumns[col1],bothcolumns[col2]]]
                    else:
                        repldict[bothcolumns[col3]]=[[bothcolumns[col1],bothcolumns[col2]]]
        #print "\n",i,"expressions from",fname,"have been added to the replacement list"
    return repldict



def main():
    complrepldict=OrderedDict()
    # STEP 1.1: add all multi-word expressions from a dictionary of the language in question ('s ochtends --> 's_ochtends)
    alldutchwords=[line.strip() for line in open(nlwoordenbestand,mode="r",encoding="utf-8")]
    complrepldict.update(replacespaces(alldutchwords))

    # STEP 1.2: add all own rules (column 0 and 1 from user-generated TAB file)
    complrepldict.update(replaceown(ownreplacements,0,1))
    # STEP 1.3: save output to general replacement list
    with open(outputbestand,mode="w",encoding="utf-8") as fo:
        fo.write(unicode(json.dumps(complrepldict,ensure_ascii=False)))
    print "\nFinished writing",outputbestand
    print "YOU'RE READY WITH THE GENERAL REPLACEMENT LIST!\n"

    # STEP 2.1: Add rules that only have to be replaced if already one replacement according to rule above has taken
    # place. Example: Jan Smit is replaced by jan_smit (1.2), now, also subsequent mentions of Smit (without Jan)
    # should be replaced by jan_smit
    complrepldict2=OrderedDict()
    complrepldict2.update(replaceownlistoutput(ownreplacements,2,1))
    # STEP 2.2: save output to second-mention-output file
    with open(outputbestand2,mode="w",encoding="utf-8") as fo:
        fo.write(unicode(json.dumps(complrepldict2,ensure_ascii=False)))
    print "\nFinished writing",outputbestand2
    print "YOU'RE READY WITH THE REPLACEMENT LIST FOR SECOND MENTIONS (e.g., LAST NAMES/FULL NAMES)!\n"


    # STEP 3.1: Add rules for replacements that only have to take place if some other expression occurs in the article
    complrepldict3=OrderedDict()
    complrepldict3.update(replaceownindien(ownreplacements,2,1,3))
    
    with open(outputbestand3,mode="w",encoding="utf-8") as fo:
        fo.write(unicode(json.dumps(complrepldict3,ensure_ascii=False)))
    
    print "\nFinished writing",outputbestand3
    print "YOU'RE READY WITH THE REPLACEMENT LIST FOR REPLACEMENTST IN CASE OF INDICATORS BEING PRESENT!\n"


    
if __name__ == "__main__":
    main()
