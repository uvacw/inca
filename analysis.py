#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from io import open
#from pymongo import MongoClient, Connection, TEXT
import pymongo
import argparse
import configparser
from collections import Counter, defaultdict
import sys
from nltk.stem import SnowballStemmer
from itertools import combinations, chain
import ast
from numpy import log
from gensim import corpora, models, similarities
import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn.decomposition import PCA
import os
# from scipy.spatial.distance import cosine
from sklearn import preprocessing
from sklearn.cluster import KMeans

# TODO
# bedrijf minimaal twee keer genoemd
# sentimentanalysescores worden nu bij LDA opgeslagen, niet bij cluster en PCA. indien nodig, nog toevoegen

# read config file and set up MongoDB
config = configparser.RawConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/config.conf')
dictionaryfile=config.get('files','dictionary')
networkoutputfile=config.get('files','networkoutput')
lloutputfile=config.get('files','loglikelihoodoutput')
lloutputcorp1file=config.get('files','loglikelihoodoutputoverrepcorp1')
cosdistoutputfile=config.get('files','cosdistoutput')
compscoreoutputfile=config.get('files','compscoreoutput')
clusteroutputfile=config.get('files','clusteroutput')
ldaoutputfile=config.get('files','ldaoutput')
ldatopicfile=config.get('files','ldaoutputtopics')
databasename=config.get('mongodb','databasename')
collectionname=config.get('mongodb','collectionname')
#collectionnamecleaned=config.get('mongodb','collectionnamecleaned')
#collectionnamecleanedNJR = config.get('mongodb','collectionnamecleanedNJR')
username=config.get('mongodb','username')
password=config.get('mongodb','password')
client = pymongo.MongoClient(config.get('mongodb','url'))
db = client[databasename]
db.authenticate(username,password)
collection = db[collectionname]
#collectioncleaned = db[collectionnamecleaned]




def removezerovariance(A):
    '''
    Takes a numpy array as input and removes all rows and columns with zero variance
    '''

    colvar=A.var(0)
    rowvar=A.var(1)
    colvaris0=np.equal(colvar, np.zeros(1))
    rowvaris0=np.equal(rowvar, np.zeros(1))

    i=0
    colindices=[]
    for bo in colvaris0:
        if bo == True:
            colindices.append(i)

    i+=1

    i=0
    rowindices=[]
    for bo in rowvaris0:
        if bo == True:
            rowindices.append(i)

    i+=1

    print("Removing the following rows because they have zero variance:",rowindices)
    print("Removing colums because they have zero variance:",colindices)

    A = np.delete(A, (rowindices), axis=0)
    A = np.delete(A, (colindices), axis=1)
    return A






def stemmed(text,language):
    stemmer= SnowballStemmer(language)
    tas=text.split()
    text=""
    for word in tas:
        text=" ".join((text,stemmer.stem(word)))
    return text.lstrip()



def split2ngrams(txt, n):
    if n==1:
        return txt.split()
    else:
        return [tuple(txt.split()[i:i+n]) for i in range(len(txt.split())-(n-1))]


def frequencies_nodict():
    '''
    returns a counter object of word frequencies
    '''
    if ngrams!= 1:
         print("This function does not make sense to run with ngrams, ignoring the argument.")

    # .replace is nodig omdat we ervan uitgaan dat alle spaties in de tekst door "_" zijn vervangen (met de clean-functie)
    # maar in een tweede stap is _ weggehaald, dus hier vervangen door "" ipv "_"
    if stemming==0:
        knownwords = set([line.strip().replace(" ","").lower() for line in open(dictionaryfile,mode="r",encoding="utf-8")])
    else:
        knownwords = set([stemmed(line.strip().replace(" ","").lower(),stemming_language) for line in open(dictionaryfile,mode="r",encoding="utf-8")])

    all=collection.find(subset,{'text': 1, "_id":0})
    aantal=all.count()
    #print all[50]["text"]
    unknown=[]
    i=0
    for item in all:
       i+=1
       print("\r",i,"/",aantal," or ",int(i/aantal*100),"%", end=' ')
       sys.stdout.flush()

       if stemming==0:
           unknown+=[woord for woord in item['text'].split() if woord not in knownwords]
       else:
           unknown+=[woord for woord in stemmed(item['text'],stemming_language).split() if woord not in knownwords]
    c=Counter(unknown)
    print()
    return c



def frequencies():
    '''
    returns a counter object of word frequencies
    '''
    
    all=collection.find(subset,{'text': 1, "_id":0})
    aantal=all.count()
    # print all[50]["text"]
    c=Counter()
    i=0
    for item in all:
        i+=1
        print("\r",i,"/",aantal," or ",int(i/aantal*100),"%", end=' ')
        sys.stdout.flush()
        if 'text' in item:    # only proceed if there is a 'text' key in the item
            if stemming==0:
                c.update([woord for woord in split2ngrams(item['text'],ngrams)]) 
            else:
                c.update([woord for woord in split2ngrams(stemmed(item['text'],stemming_language),ngrams)])  
        else:
            continue
    print()
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
    
    cooc=defaultdict(int)
    
    print("Determining the",n,"most frequent words...\n")
    c=frequencies()
    topnwords=set([a for a,b in c.most_common(n)])
   
    all=collection.find(subset,{'text': 1, "_id":0})
    aantal=all.count()
    
    print("\n\nDetermining the cooccurrances of these words with a minimum cooccurance of",minedgeweight,"...\n")
    i=0
    for item in all:
        i+=1
        print("\r",i,"/",aantal," or ",int(i/aantal*100),"%", end=' ')
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
                                f.write(str(k[0])+","+str(c[k[0]])+"\n")
                                algenoemd.append(k[0])
                        if k[1] not in algenoemd:
                                #f.write(k[1]+","+str(c[k[1]])+"\n")
                                f.write(str(k[1])+","+str(c[k[1]])+"\n")
                                algenoemd.append(k[1])
        for k in verwijderen:
                del cooc[k]

        f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
        for k, v in cooc.items():
                # next line is necessary for the case of ngrams (we want the INNER TUPLES (the ngrams) become strings
                k2=[str(partofngram) for partofngram in k]
                regel= ",".join(k2)+","+str(v)
                f.write(regel+"\n")

    print("\nDone. Network file written to",networkoutputfile)
    





def llcompare(corpus1,corpus2,llbestand,llbestand2):
    # llbestand: full output
    # llbestand2: only the words that are overrepresented in corpus 1, in the order of their loglikelihood
    # using the same terminology as the cited paper:
    # a = freq in corpus1
    # b = freq in corpus2
    # c = number of words corpus1
    # d = number of words corpus2
    # e1 = expected value corpus1
    # e2 = expected value corpus2

    c = len(corpus1)
    d = len(corpus2)
    ll={}
    e1dict={}
    e2dict={}
    
    for word in corpus1:
        a=corpus1[word]
        try:
            b=corpus2[word]
        except KeyError:
            b=0
        e1 = c * (a + b) / (c + d)
        e2 = d * (a + b) / (c + d)
        # llvalue=2 * ((a * log(a/e1)) + (b * log(b/e2)))
        # if b=0 then (b * log(b/e2)=0 and NOT nan. therefore, we cannot use the formula above
        if a==0:
            part1=0
        else:
            part1=a * log(a/e1)
        if b==0:
            part2=0
        else:        
            part2=b * log(b/e2)
        llvalue=2*(part1 + part2)
        ll[word]=llvalue
        e1dict[word]=e1
        e2dict[word]=e2
    
    for word in corpus2:
        if word not in corpus1:
            a=0
            b=corpus2[word]
            e2 = d * (a + b) / (c + d)
            llvalue=2 * (b * log(b/e2))
            ll[word]=llvalue
            e1dict[word]=0
            e2dict[word]=e2
    print("Writing results...")
    with open(llbestand, mode='w', encoding="utf-8") as f, open(llbestand2, mode='w', encoding="utf-8") as f2:
            f.write("ll,word,freqcorp1,expectedcorp1,freqcorp2,expectedcorp2\n")
            for word,value in sorted(iter(ll.items()), key=lambda word_value: (word_value[1], word_value[0]), reverse=True):
                    # print value,word
                    try:
                            freqcorp1=corpus1[word]
                    except KeyError:
                            freqcorp1=0
                    try:
                            freqcorp2=corpus2[word]
                    except KeyError:
                            freqcorp2=0
                    e1=str(e1dict[word])
                    e2=str(e2dict[word])
                    f.write(str(value)+","+word+","+str(freqcorp1)+","+e1+","+str(freqcorp2)+","+e2+"\n")
                    # if the word is OVERrepresented in corp 1 (observed > expected), then it is also written in llbestand2
                    if freqcorp1>e1dict[word]: f2.write(word+"\n")
    print("Output written to",llbestand)
    print("Those words whith observed frequency > expected frequency in Corpus 1 are additionally (sorted by descending LL) written to",llbestand2)



def ll():
    corpus1=frequencies()
    print(len(corpus1))
    global subset
    subsetbak=subset
    subset=subset2
    corpus2=frequencies()
    print(len(corpus2))
    subset=subsetbak
    llcompare(corpus1,corpus2,lloutputfile,lloutputcorp1file)




def lda(minfreq,file,ntopics,):
    c=frequencies()
    all=collection.find(subset)

    try:
        allterms=subset['$text']['$search'].decode("utf-8").split()
    except:
        # voor het geval dat er geen zoektermen zijn gebruikt
        allterms=[]
    allterms+=extraterms
    foroutput_alltermslabels="\t".join(allterms)
    foroutput_alltermscounts=[]
    foroutput_alltermsfirstocc=[]
    foroutput_alltermsfirstocclabels='\t'.join(['pos_'+t for t in allterms])

    foroutput_source=[]
    #foroutput_source2=[]
    #TODO ook bij andere methodes source2 opslaan, niet alleen in LDA module
    foroutput_firstwords=[]
    foroutput_id=[]
    foroutput_byline = []
    foroutput_section = []
    foroutput_length = []
    foroutput_language = []
    foroutput_pubdate_day = []
    foroutput_pubdate_month = []
    foroutput_pubdate_year = []
    foroutput_pubdate_dayofweek = []
    foroutput_pubdate_weeknr = []
    foroutput_subjectivity=[]
    foroutput_polarity=[]
    for item in all:
        if 'text' in item:   # do not proceed if article has no text
            foroutput_firstwords.append(item["text"][:20])
            foroutput_source.append(item["source"])
            #foroutput_source2.append(item["source2"])
            foroutput_id.append(item["_id"])
            try:
                foroutput_byline.append(item["byline"])
            except:
                foroutput_byline.append('N/A')
            try:
                foroutput_section.append(item["section"])
            except:
                foroutput_section.append('N/A') 
            # seperate section and pagenumber instead, tailored to Dutch Lexis Nexis
            # sectie=item["section"].split(";")
            #foroutput_section.append(sectie[0]+"\t"+sectie[1].strip("blz. "))
            # end
            foroutput_length.append(str(item["length_char"]))
            #foroutput_language.append(item["language"])
            foroutput_language.append('dutch')
            foroutput_pubdate_day.append(str(item["datum"].day))
            foroutput_pubdate_month.append(str(item["datum"].month))
            foroutput_pubdate_year.append(str(item["datum"].year))
            foroutput_pubdate_dayofweek.append(str(item["datum"].weekday()))
            foroutput_pubdate_weeknr.append(item['datum'].strftime('%U'))
            foroutput_subjectivity.append('0')
            foroutput_polarity.append('0')
            termcounts=""
            for term in allterms:
                termcounts+=("\t"+str(item["text"].split().count(term)))
            foroutput_alltermscounts.append(termcounts)
            termoccs=''
            for term in allterms:
                termoccs+=('\t'+str(item['text'].find(term)))
            foroutput_alltermsfirstocc.append(termoccs)
        else:
            continue



    # TODO: integreren met bovenstaande code, nu moet .find nog een keer worden opgeroepen aangezien het een generator is
    all=collection.find(subset)


    if stemming==0:
        # oude versie zonder ngrams: texts =[[word for word in item["text"].split()] for item in all]
        texts =[[word for word in split2ngrams(item["text"],ngrams)] for item in all if 'text' in item]
    else:
        texts =[[word for word in split2ngrams(stemmed(item["text"],stemming_language),ngrams)] for item in all if 'text' in item]

    if minfreq>0 and file=="":
        # unicode() is neccessary to convert ngram-tuples to strings
        texts =[[str(word) for word in text if c[word]>=minfreq] for text in texts]

    elif minfreq==0 and file!="":
        allowedwords=set(line.strip().lower() for line in open(file,mode="r",encoding="utf-8"))
        # unicode() is neccessary to convert ngram-tuples to strings
        texts =[[str(word) for word in text if word in allowedwords] for text in texts]


    # TODO NU WORDEN DE EXTRA TERMS (indien gedefinieerd) NIET meegenomen om de topics te bepalen
    # TODO hier moet een keuzemogelijkheid komen; ook moeten we kijken of dit ueberhaupt zinvol is

    if not extraterms==[]:
        texts = [[" ".join([w for w in t.split() if w not in set(extraterms)]) for t in tt] for tt in texts]


    # Create Dictionary.
    id2word = corpora.Dictionary(texts)

    # Creates the Bag of Word corpus.
    mm =[id2word.doc2bow(text) for text in texts]
    # Trains the LDA models.
    # lda = models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=ntopics, update_every=1, chunksize=10000, passes=1)
    lda = models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=ntopics, alpha="auto")
    # Prints the topics.
    for top in lda.print_topics(num_topics=ntopics, num_words=5):
        print("\n",top)


    print("\nFor further analysis, a dataset with the topic score for each document is saved to",ldaoutputfile)
    i=0

    scoresperdoc=lda.inference(mm)


    with open(ldaoutputfile,"w",encoding="utf-8") as fo:
        topiclabels=""
        for j in range(ntopics):
            topiclabels+=("\tTopic"+str(j+1))
        fo.write('id\t'+'source\t'+'firstwords\t'+'byline\t'+'section\t'+'length\t'+'language\t'+'polarity\tsubjectivity\t'+'pubdate_day\t'+'pubdate_month\t'+'pubdate_year\t'+'pubdate_dayofweek\tpubdate_weeknr'+topiclabels+"\t"+foroutput_alltermslabels+"\t"+foroutput_alltermsfirstocclabels+"\n")
        for row in scoresperdoc[0]:
            #print type(row)
            #regel=row.tolist()
            #print len(regel)
            #print type(regel)
            #print regel
            fo.write(str(foroutput_id[i])+'\t'+foroutput_source[i]+'\t'+foroutput_firstwords[i]+'\t'+foroutput_byline[i]+'\t'+foroutput_section[i]+'\t'+foroutput_length[i]+'\t'+foroutput_language[i]+'\t'+foroutput_polarity[i]+'\t'+foroutput_subjectivity[i]+'\t'+foroutput_pubdate_day[i]+'\t'+foroutput_pubdate_month[i]+'\t'+foroutput_pubdate_year[i]+'\t'+foroutput_pubdate_dayofweek[i]+'\t'+foroutput_pubdate_weeknr[i]+'\t')

            fo.write('\t'.join(["{:0.3f}".format(loading) for loading in row]))
            fo.write(foroutput_alltermscounts[i])
            fo.write(foroutput_alltermsfirstocc[i])
            fo.write("\n")
            i+=1

    print('Also saving the topics themselves at {} ...'.format(ldatopicfile))

    with open(ldatopicfile,'w',encoding='utf-8') as fo:
        topics=lda.top_topics(mm, num_words=20)
        toplist=[]
        for topic in topics[0:20]:
            top=[]    
            for t in topic[0]:
                top.append(t[1])
            top.append(topic[1])
            toplist.append(top)
            fo.write("\n\nTopic")        
            for outtext in toplist:
                fo.write("--------------------------\n\n")            
                for t in outtext:
                    fo.write(str(t)+ " ")




def tfcospca(n,file,comp,varimax):
    '''
    n = N most frequent words to include
    file = alternative to n, use words from inputfile file
    comp = number of components or, if 0<n<1, min eigenvalue of each component
    varimax = bool to indicate whether a varimax rotation should be performed 
    '''

    if n>0 and file=="":
        c=frequencies()
        topnwords=[a for a,b in c.most_common(n)]
    elif n==0 and file!="":
        topnwords=[line.strip().lower() for line in open(file,mode="r",encoding="utf-8")]
    
    #all=collectioncleaned.find(subset,{"text": 1, "_id":1, "source":1})
    all=collection.find(subset)
    # TF=np.empty([n,n-1])
    docs=[]
    foroutput_source=[]
    foroutput_firstwords=[]
    foroutput_id=[]
    foroutput_byline = []
    foroutput_section = []
    foroutput_length = []
    foroutput_language = []
    foroutput_pubdate_day = []
    foroutput_pubdate_month = []
    foroutput_pubdate_year = []
    foroutput_pubdate_dayofweek = []
    try:
        allterms=subset['$text']['$search'].decode("utf-8").split()
    except:
        # voor het geval dat er geen zoektermen zijn gebruikt
        allterms=[]    
    allterms+=extraterms
    foroutput_alltermslabels="\t".join(allterms)
    foroutput_alltermscounts=[]

    for item in all:
        foroutput_firstwords.append(item["text"][:20])
        foroutput_source.append(item["source"])
        foroutput_id.append(item["_id"])
        foroutput_byline.append(item["byline"])
        foroutput_section.append(item["section"])
        # seperate section and pagenumber instead, tailored to Dutch Lexis Nexis
        # sectie=item["section"].split(";")
        #foroutput_section.append(sectie[0]+"\t"+sectie[1].strip("blz. "))
        # end
        foroutput_length.append(item["length"])
        foroutput_language.append(item["language"])
        foroutput_pubdate_day.append(item["pubdate_day"])
        foroutput_pubdate_month.append(item["pubdate_month"])
        foroutput_pubdate_year.append(item["pubdate_year"])
        foroutput_pubdate_dayofweek.append(item["pubdate_dayofweek"])
        termcounts=""
        for term in allterms:
            termcounts+=("\t"+str(item["text"].split().count(term)))
        foroutput_alltermscounts.append(termcounts)
        if stemming==0:
            c_item=Counter(split2ngrams(item["text"],ngrams))
        else:
            c_item=Counter(split2ngrams(stemmed(item["text"],stemming_language),ngrams))
        tf_item=[]
        for word in topnwords:
            tf_item.append(c_item[word])
        docs.append(tf_item)

    TF=np.array(docs).T
    print("\n\nCreated a {} by {} TF-document matrix which looks like this:".format(*TF.shape))
    print(TF)
    COSDIST = 1-pairwise_distances(TF, metric="cosine") 
    print("\nAs a {} by {} cosine distance matrix, it looks like this:".format(*COSDIST.shape))
    print(COSDIST)

    COSDIST=removezerovariance(COSDIST)

    print("\nConducting a principal component analysis...")
    # method following http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
    pca = PCA(n_components=comp)
    # volgende regel zou eigenlijk overbodig moeten zijn, zouden niet moeten standardiseren (alles toch op dezelfde schaal gemeten + cosinus-transformatie gedaan), maar in het kader van vergelijkbaarheid met SPSS/STATA/R-output doen we het toch...
    # zonder deze regel krijk je wel hele rare eigenvalues... (logisch ook, aangezien de varianties anders zijn!)
    COSDIST=preprocessing.scale(COSDIST)
    pca.fit(COSDIST)
    # wel te repiceren in stata met pca *, components(3) covariance , SPSS Heeft wat afwijkingen maar klopt in principe ook als je covariance ipv correlation matrix kiest
    
    print("\nExplained variance of each component:",pca.explained_variance_ratio_)
    print("\nEigenvalue of each component:",pca.explained_variance_,"\n")
    #loadings= pca.transform(COSDIST).tolist()
    #print len(pca.transform(COSDIST).tolist())
    
    loadings= pca.components_.T.tolist()   # let ook hier op het transposen 
    if varimax:
        # TODO eigenvalues of rotated component matrix. Could work with this: http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.eigvals.html#numpy.linalg.eigvals , but for that, the matrix must have a square shape. I guess we'd have to retrieve the full PCA with _ALL_ components then
        print("NB: The explained variance and the eigenvalues above refer to the unrotated components. Their calculation for the rotated components has not been implemented yet. For the time being, you can open the cosine distance file (which will be created in a minute) in STATA and run the 'pca' and 'rotate' commands, which should give exactly the same results as displayed below, but include the eigenvalues and explained variance for the rotated components as well.\n")
        loadings=rotvarimax(pca.components_.T).tolist()
        print("\nThe rotated component loadings (varimax) are:")

    else:
        loadings= pca.components_.T.tolist()   # let ook hier op het transposen 
        print("\nThe component loadings are:")


    i=0
    for row in loadings:
        print(topnwords[i],"\t\t", end=' ')
        print('\t'.join(["{:.3f}".format(loading) for loading in row])) 
        i+=1
    i=0
    
    
    '''
    We could print the transformed scores, but that's of little interest, so let's skip that
    print "\n\nThe transformed scores are:"
    scores=np.dot(COSDIST,loadings)
    
    for row in scores:
        print topnwords[i],"\t\t",
        print '\t'.join(["{:.3f}".format(loading) for loading in row]) 
        i+=1
    '''

    # save loadings to a dataset
    print("\nFor further analysis, a dataset with the component loadings for each document is saved to",compscoreoutputfile)
    i=0

    scoresperdoc=np.dot(TF.T,loadings)

    with open(compscoreoutputfile,"w",encoding="utf-8") as fo:
        pcalabels=""
        for j in range(len(loadings[0])):
            pcalabels+=("\tComp"+str(j+1))
        fo.write('id\t'+'source\t'+'firstwords\t'+'byline\t'+'section\t'+'length\t'+'language\t'+'pubdate_day\t'+'pubdate_month\t'+'pubdate_year\t'+'pubdate_dayofweek'+pcalabels+"\t"+foroutput_alltermslabels+"\n")
        for row in scoresperdoc:
            fo.write(str(foroutput_id[i])+'\t'+foroutput_source[i]+'\t'+foroutput_firstwords[i]+'\t'+foroutput_byline[i]+'\t'+foroutput_section[i]+'\t'+foroutput_length[i]+'\t'+foroutput_language[i]+'\t'+foroutput_pubdate_day[i]+'\t'+foroutput_pubdate_month[i]+'\t'+foroutput_pubdate_year[i]+'\t'+foroutput_pubdate_dayofweek[i]+'\t')
            fo.write('\t'.join(["{:0.3f}".format(loading) for loading in row]))
            fo.write(foroutput_alltermscounts[i])
            fo.write("\n")
            i+=1

    print("\nFor further analysis, a copy of the cosine distance matrix is saved to",cosdistoutputfile)
    # hiervoor heb je numpy > 1.7 nodig (vanwege header)
    #np.savetxt(cosdistoutputfile,COSDIST,fmt=str("%.6f"),delimiter=",",header=",".join(topnwords))
    # om te voorkomen dat numpy 1.7 of hoger nodig is, workaround zonder "header"
    np.savetxt(cosdistoutputfile+"TEMP",COSDIST,fmt=str("%1.6f"),delimiter=",")
    with open(cosdistoutputfile,"w",encoding="utf-8") as fo:
        fo.write(",".join([str(item) for item in topnwords]))
        fo.write("\n")
        with open (cosdistoutputfile+"TEMP","r",encoding="utf-8") as fi:
            fo.write(fi.read())
    os.remove(cosdistoutputfile+"TEMP")


def rotvarimax(Phi, gamma = 1.0, q = 20, tol = 1e-6):
    # see http://stackoverflow.com/questions/17628589/perform-varimax-rotation-in-python-using-numpy and http://en.wikipedia.org/wiki/Talk%3aVarimax_rotation
    from numpy import eye, asarray, dot, sum, diag
    from numpy.linalg import svd
    p,k = Phi.shape
    R = eye(k)
    d=0
    for i in range(q):
        d_old = d
        Lambda = dot(Phi, R)
        u,s,vh = svd(dot(Phi.T,asarray(Lambda)**3 - (gamma/p) * dot(Lambda, diag(diag(dot(Lambda.T,Lambda))))))
        R = dot(u,vh)
        d = sum(s)
        if d_old!=0 and d/d_old < tol: break
    print("The following Component Transformation Matrix has been determined for the rotation:")
    print(R)
    return dot(Phi, R)





def kmeans(n,file,noclusters,normalize):
    '''
    n = N most frequent words to include
    file = alternative to n, use words from inputfile file
    nocluster = number of clusters
    '''

    if n>0 and file=="":
        c=frequencies()
        topnwords=[a for a,b in c.most_common(n)]
    elif n==0 and file!="":
        topnwords=[line.strip().lower() for line in open(file,mode="r",encoding="utf-8")]

    all=collection.find(subset)
    docs=[]
    foroutput_source=[]
    foroutput_firstwords=[]
    foroutput_id=[]
    foroutput_byline = []
    foroutput_section = []
    foroutput_length = []
    foroutput_language = []
    foroutput_pubdate_day = []
    foroutput_pubdate_month = []
    foroutput_pubdate_year = []
    foroutput_pubdate_dayofweek = []

    try:
        allterms=subset['$text']['$search'].decode("utf-8").split()
    except:
        # voor het geval dat er geen zoektermen zijn gebruikt
        allterms=[]
    allterms+=extraterms
    foroutput_alltermslabels="\t".join(allterms)
    foroutput_alltermscounts=[]

    for item in all:
        foroutput_firstwords.append(item["text"][:20])
        foroutput_source.append(item["source"])
        foroutput_id.append(item["_id"])
        foroutput_byline.append(item["byline"])
        foroutput_section.append(item["section"])
        # seperate section and pagenumber instead, tailored to Dutch Lexis Nexis
        # sectie=item["section"].split(";")
        #foroutput_section.append(sectie[0]+"\t"+sectie[1].strip("blz. "))
        # end
        foroutput_length.append(item["length"])
        foroutput_language.append(item["language"])
        foroutput_pubdate_day.append(item["pubdate_day"])
        foroutput_pubdate_month.append(item["pubdate_month"])
        foroutput_pubdate_year.append(item["pubdate_year"])
        foroutput_pubdate_dayofweek.append(item["pubdate_dayofweek"])
        termcounts=""
        for term in allterms:
            termcounts+=("\t"+str(item["text"].split().count(term)))
        foroutput_alltermscounts.append(termcounts)
        if stemming==0:
            c_item=Counter(split2ngrams(item["text"],ngrams))
        else:
            c_item=Counter(split2ngrams(stemmed(item["text"],stemming_language),ngrams))
        tf_item=[]
        for word in topnwords:
            tf_item.append(c_item[word])
        docs.append(tf_item)

    TF=np.array(docs)   # let op, in tegenstelling tot de PCA hier niet transposen (.T), want we willen niet de variabelen clusteren maar de documenten

    if normalize:
        TF=preprocessing.normalize(TF.astype((float)),axis=0)

    from sklearn import metrics

    km = KMeans(n_clusters=noclusters, init='k-means++', max_iter=100, n_init=1, verbose=True)

    clustersolution=km.fit_predict(TF)

    #print "Homogeneity: %0.3f" % metrics.homogeneity_score(labels, km.labels_)
    #print "Completeness: %0.3f" % metrics.completeness_score(labels, km.labels_)
    #print "V-measure: %0.3f" % metrics.v_measure_score(labels, km.labels_)
    #print "Adjusted Rand-Index: %.3f" % metrics.adjusted_rand_score(labels, km.labels_)
    #print "Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, sample_size=1000)

    print("Cluster sizes:")
    counts=np.bincount(clustersolution)
    print("         \tFreq\t%")
    i=0
    for count in counts:
        print("Cluster\t",i,"\t",count,"\t","{:.2f}".format(100*count/len(foroutput_id)))
        i+=1

    print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    #terms = vectorizer.get_feature_names()
    #terms=topnwords
    for i in range(noclusters):
        print("Cluster %d:" % i)
        for ind in order_centroids[i, :10]:
            print(' %s' % topnwords[ind])
    print()

    print("The cluster centers are:")

    clusterlabels="\t"
    for j in range(noclusters):
        clusterlabels+=("\tClu."+str(j))
    print(clusterlabels)
    loadings=km.cluster_centers_.T
    i=0
    for row in loadings:
        print(topnwords[i],"\t\t", end=' ')
        print('\t'.join(["{:.3f}".format(loading) for loading in row]))
        i+=1
    i=0

    # save clusters to a dataset
    print("\nFor further analysis, a dataset with the cluster number for each document is saved to",clusteroutputfile)


    with open(clusteroutputfile,"w",encoding="utf-8") as fo:
        fo.write('id\t'+'source\t'+'firstwords\t'+'byline\t'+'section\t'+'length\t'+'language\t'+'pubdate_day\t'+'pubdate_month\t'+'pubdate_year\t'+'pubdate_dayofweek\t'+'Cluster\t'+foroutput_alltermslabels+"\n")
        for i in range(len(foroutput_id)):
            fo.write(str(foroutput_id[i])+'\t'+foroutput_source[i]+'\t'+foroutput_firstwords[i]+'\t'+foroutput_byline[i]+'\t'+foroutput_section[i]+'\t'+foroutput_length[i]+'\t'+foroutput_language[i]+'\t'+foroutput_pubdate_day[i]+'\t'+foroutput_pubdate_month[i]+'\t'+foroutput_pubdate_year[i]+'\t'+foroutput_pubdate_dayofweek[i]+'\t'+str(clustersolution[i]))
            fo.write(foroutput_alltermscounts[i])
            fo.write("\n")
            cl=int(clustersolution[i])
            collection.update({'_id':foroutput_id[i]},{'$set':{'cluster':cl}},upsert=False)




def main():
    parser=argparse.ArgumentParser("This program is part of VETTE NAAM BEDENKEN EN ZO VERDER")
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--frequencies",metavar="N",help="List the N most common words")
    group.add_argument("--frequencies_nodict",metavar="N",help="List the N most common words, but only those which are NOT in the specified dictionary (i.e., list all non-dutch words)")
    group.add_argument("--lda",metavar=("N1","N2"),help="Perform a Latent Diriclet Allocation analysis  based on words with a minimum frequency of N1 and generate N2 topics",nargs=2)
    group.add_argument("--lda_ownwords",metavar=("FILE","N"),help="Perform a Latent Diriclet Allocation analysis  based on words in FILE and generate N topics",nargs=2)
    group.add_argument("--ll",help="Compare the loglikelihood of the words within the subset with the whole dataset",action="store_true")
    group.add_argument("--network",metavar=("N1","N2"),help="Create .gdf network file to visualize word-cooccurrances of the N1 most frequently used words with a minimum edgeweight of N2. E.g.: --network 200 50",nargs=2)
    group.add_argument("--pca",metavar=("N1","N2"),help="Create .a document-tf- matrix with all selected articles and the N1 most frequent words, transform it to a cosine dissimilarity matrix and carry out a principal component analysis, resulting in N2 components",nargs=2)
    group.add_argument("--pca_ownwords",metavar=("FILE","N"),help="Create .a document-tf- matrix with all selected articles and the words stored in FILE (UTF-8, one per line), transform it to a cosine dissimilarity matrix and carry out a principal component analysis, resulting in N components. If 0<N<1, then all components, then all components with an explained variance > N are listed.",nargs=2)
    group.add_argument("--kmeans",metavar=("N1","N2"),help="Create .a document-tf- matrix with all selected articles and the N1 most frequent words, and carry out a kmeans cluster analysis, resulting in N2 clusters",nargs=2)
    group.add_argument("--kmeans_ownwords",metavar=("FILE","N"),help="Create .a document-tf- matrix with all selected articles and the words stored in FILE (UTF-8, one per line), transform it to a tf-idf matrix and carry out a kmeans cluster analysis, resulting in N clusters.",nargs=2)
    group.add_argument("--search", metavar="SEARCHTERM",help="Perform a simple search, no further options possible. E.g.:  --search hema")
    parser.add_argument("--subset", help="Use MongoDB-style .find() filter in form of a Python dict. E.g.:  --subset=\"{'source':'de Volkskrant'}\" or --subset=\"{'\\$text':{'\\$search':'hema'}}\" or a combination of both: --subset=\"{'\\$text':{'\\$search':'hema'}}\",'source':'de Volkskrant'}\"")
    # ander voorbeeld: --subset="{'section':{'\$regex':'[Ee]conom'},'suspicious':False}"
    parser.add_argument("--subset2", help="Compare the first subset specified not to the whole dataset but to another subset. Only evaluated together with --ll.")
    parser.add_argument("--varimax", help="If specified with --pca or --pca_ownwords, a varimax rotation is performed",action="store_true")
    parser.add_argument("--normalize", help="If specified with --kmeans or --kmeans_ownwords, TF-matrix is normalized before the cluster analysis starts",action="store_true")
    parser.add_argument("--ngrams",metavar="N",help="By default, all operations are carried oud on single words. If you want to use bigrams instead, specify --ngram=2, or 3 for trigrams and so on.",nargs=1)
    parser.add_argument("--stemmer",metavar="language",help='Invokes the snowball stemming algorithm. Specify the language: --stemmer="dutch"',nargs=1)
    parser.add_argument("--extraterms",help='When a dataset that includes word frequencies of some important words in the output (e.g., after LDA), this option allows to specify a space-seperated list of words to additionally include',nargs=1)
    parser.add_argument("--njronly",help="Use cleaned database with nouns, adjectives, and adverbs only, if created",action="store_true")
    # parser.add_argument("--search", help="Use MongoDB-style text search in form of a Python dict. E.g.:  --subset \"{'\\$text':{'\\$search':'hema'}}\"")
    



    '''
    TODO TEXT SEARCH
    ---search
    FILTEREN OP ZOEKTERMEN
    http://blog.mongodb.org/post/52139821470/integrating-mongodb-text-search-with-a-python-app
    '''


    args=parser.parse_args()
    global ngrams
    if not args.ngrams:
        ngrams=1
    else:
        ngrams=int(args.ngrams[0])

    global stemming
    global stemming_language
    if not args.stemmer:
        stemming=0
    else:
        stemming=1
        stemming_language=args.stemmer[0]




    # TODO ENABLE TO USE textcleannjr instead of textclean of text

    print("Ensure that the articles are properly indexed...")
    collection.ensure_index([("text", pymongo.TEXT)], cache_for=300,default_language="nl",language_override="nl")
    print("Done building index.")

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

        print("Analysis will be based on a dataset filterd on",subset)


    global subset2
    if not args.subset2:
        subset2={}
    else:
        try:
            subset2=ast.literal_eval(args.subset2)
        except:
            print("You specified an invalid filter for subset2!")
            sys.exit()

        if type(subset2) is not dict:
            print("You specified an invalid filter for subset2!")
            sys.exit()
        print("Subset to compare with is",subset2)


    global extraterms
    if not args.extraterms:
            extraterms=[]
    else:
            extraterms=args.extraterms[0].split()

    if args.search:
        query=db.command('text',collectionnamecleaned,search=args.search, language="nl")
        print("Finished with search,",len(query["results"]),"matching articles found.")
        print("Some stats:",query["stats"])
        print("relevance\tsource\tdate")
        for results in query["results"]:
            print(results["score"],"\t",results["obj"]["source"],"\t",results["obj"]["date"])


    if args.ll:
        ll()

    if args.lda:
        lda(int(args.lda[0]),"",int(args.lda[1]))

    if args.lda_ownwords:
        lda(0,args.lda_ownwords[0],int(args.lda_ownwords[1]))

    if args.pca:
        tfcospca(int(args.pca[0]),"",float(args.pca[1]),args.varimax)
        
    if args.pca_ownwords:
        tfcospca(0,args.pca_ownwords[0],float(args.pca_ownwords[1]),args.varimax)

    if args.kmeans:
        kmeans(int(args.kmeans[0]),"",int(args.kmeans[1]),args.normalize)

    if args.kmeans_ownwords:
        kmeans(0,args.kmeans_ownwords[0],int(args.kmeans_ownwords[1]),args.normalize)




    if args.frequencies:
        c=frequencies()
        for k,v in c.most_common(int(args.frequencies)):
            print(v,"\t",k)
            # willen we de woorden nog opslaan? zo ja, iets toevoegen zoals hieronder. of met set() als we de duplicaten eruit willen halen
            '''
            with open(outputbestand,"w", encoding="utf-8") as f:
            for woord in belangrijk:
            f.write(woord+"\n")
            '''



    if args.frequencies_nodict:
        c=frequencies_nodict()
        for k,v in c.most_common(int(args.frequencies_nodict)):
            print(v,"\t",k)
            # willen we de woorden nog opslaan? zo ja, iets toevoegen zoals hieronder. of met set() als we de duplicaten eruit willen halen
            '''
            with open(outputbestand,"w", encoding="utf-8") as f:
            for woord in belangrijk:
            f.write(woord+"\n")
            '''

    if args.network:
        coocnet(int(args.network[0]),int(args.network[1]))



if __name__ == "__main__":
    main()
