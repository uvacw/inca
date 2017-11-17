'''
This file provides importing functionality
'''
from core.document_class import Document
import datetime
import logging
logger = logging.getLogger(__name__)
from core.database import config
try:
    import pymongo
except:
    logger.warning('No MongoDB support')
from os import listdir, walk
from os.path import isfile, join, splitext
import re


    
class importer(Document):
    '''
    This object is used to import documents
    '''


    def run(self, input_iterable, doctype_field, input_description="unknown source", id_field=None, force=False):
        '''imported from external source'''

        self.version = '.1'
        self.functiontype = 'importer'
        self.date = datetime.datetime(year=2016, month=7, day=27)

        for num,document in enumerate(input_iterable):
            logger.info('processing {num}'.format(**locals()))
            self.doctype = document.get(doctype_field, doctype_field)
            document = self._add_metadata(document)
            self._verify(document)
            if id_field and id_field in document.keys():
                document['_id'] = str(document.get(id_field, None))  #DO WE REALY WANT THIS? "None" as string?
            try:
                self._save_document(document,forced=force)
            except Exception as e:
                logger.warning("ACK, unable to import document number {num}: {e}".format(**locals()))


class mongoimporter(importer):
    '''
    This is an importer to import old-style INCA databases in MongoDB format
    '''

    def run(self, query = {}, force=False, authenticate=False):
        '''imported from MongoDB'''

        self.version = '.1'
        self.functiontype = 'importer'
        self.date = datetime.datetime(year=2017, month=4, day=4)

        databasename=config.get('mongodb','databasename')
        collectionname=config.get('mongodb','collectionname')
        username=config.get('mongodb','username')
        password=config.get('mongodb','password')
        client = pymongo.MongoClient(config.get('mongodb','url'))
        db = client[databasename]
        if authenticate:
            db.authenticate(username,password)
        collection = db[collectionname]

        mapping = {'doctype':'source',
                   'url':'url',
                   '_id':'rssidentifier',
                   'publication_date':'datum',
                   'text':'text',
                   'teaser':'teaser',
                   'title':'title',
                   'byline':'byline',
                   'bylinesource':'bylinesource',
                   'category':'section',
                   'url':'url'}
        
        input_iterable = collection.find(query)

        
        for num,inputdoc in enumerate(input_iterable):
            document={}
            for k,v in mapping.items():
                try:
                    document[k] = inputdoc[v]
                except:
                    logger.debug('key {} not found'.format(k))
            logger.info('processing {num}'.format(**locals()))
            self.doctype = document.get('doctype')
            document = self._add_metadata(document)
            self._verify(document)
            # logger.debug('about to save',document)
            # print('\n'*10)
            try:
                self._save_document(document,forced=force)
                logger.debug("Stored document {} in ES".format(num))
            except Exception as e:
                logger.warning("ACK, unable to import document number {num}: {e}".format(**locals()))



class lnimporter(importer):
    '''
    This is an importer to import lexisnexis-textfiles
    '''

    def __init__(self):
        self.MONTHMAP={"January":1, "januari": 1, "February":2, "februari":2,"March":3,"maart":3,
                        "April":4, "april":4, "mei":5, "May":5, "June":6,"juni":6, "July":7, "juli":7,
                        "augustus": 8, "August":8,"september":9,"September":9, "oktober":10,"October":10,
                        "November":11,"november":11,"December":12,"december":12}


    def run(self, pathwithlnfiles , force=False):
        '''imported from newspaper database'''

        self.version = '.1'
        self.functiontype = 'importer'
        self.date = datetime.datetime(year=2017, month=11, day=17)

        self.pathwithlnfiles = pathwithlnfiles

        mapping = {'doctype':'source',
                   'publication_date':'datum',
                   'text':'text',
                   'title':'title',
                   'byline':'byline',
                    'category':'section'}

        input_iterable = self.parseln()

        
        for num,inputdoc in enumerate(input_iterable):
            document={}
            for k,v in mapping.items():
                try:
                    document[k] = inputdoc[v]
                except:
                    logger.debug('key {} not found'.format(k))
            logger.info('processing {num}'.format(**locals()))
            self.doctype = document.get('doctype')
            document = self._add_metadata(document)
            self._verify(document)
            # logger.debug('about to save',document)
            # print('\n'*10)
            try:
                self._save_document(document,forced=force)
                logger.debug("Stored document {} in ES".format(num))
            except Exception as e:
                logger.warning("ACK, unable to import document number {num}: {e}".format(**locals()))


    def parseln(self):
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

        alleinputbestanden = []
        for path, subFolders, files in walk(self.pathwithlnfiles):
            for f in files:
                if isfile(join(path, f)) and splitext(f)[1].lower() == ".txt":
                    alleinputbestanden.append(join(path, f))

        artikel = 0
        for bestand in alleinputbestanden:
            logger.info("Now processing", bestand)
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
                        pubdate_month[artikel]=str(self.MONTHMAP[matchObj2.group(2)])
                        pubdate_year[artikel]=matchObj2.group(3)
                        pubdate_dayofweek[artikel]=matchObj2.group(4)
                        firstdate=False
                    elif matchObj3 and firstdate==True:
                        pubdate_day[artikel]=matchObj3.group(2)
                        pubdate_month[artikel]=str(self.MONTHMAP[matchObj3.group(1)])
                        pubdate_year[artikel]=matchObj3.group(3)
                        pubdate_dayofweek[artikel]="NA"
                        firstdate=False
                    elif matchObj4 and firstdate==True:
                        pubdate_day[artikel]=matchObj4.group(1)
                        pubdate_month[artikel]=str(self.MONTHMAP[matchObj4.group(2)])
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
        logger.info("Done!", artikel, "articles added.")

        if not len(journal) == len(journal2) == len(loaddate) == len(section) == len(language) == len(byline) == len(length) == len(tekst) == len(pubdate_year) == len(pubdate_dayofweek) ==len(pubdate_day) ==len(pubdate_month):
            logger.warning("!!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.warning("Ooooops! Not all articles seem to have data for each field. These are the numbers of fields that where correctly coded (and, of course, they should be equal to the number of articles, which they aren't in all cases.")
            logger.warning("journal: {}".format(len(journal)))
            logger.warning("journal2: {}".format(len(journal2)))
            logger.warning("loaddate: {}".format(len(loaddate)))
            logger.warning("pubdate_day: {}".format(len(pubdate_day)))
            logger.warning("pubdate_month: {}".format(len(pubdate_month)))
            logger.warning("pubdate_year: {}".format(len(pubdate_year)))
            logger.warning("pubdate_dayofweek: {}".format(len(pubdate_dayofweek)))
            logger.warning("section: {}".format(len(section)))
            logger.warning("language: {}".format(len(language)))
            logger.warning("byline: {}".format(len(byline)))
            logger.warning("length: {}".format(len(length)))
            logger.warning("tekst: {}".format(len(tekst)))
            logger.warning("!!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.warning("Anyhow, we're gonna proceed and set those invalid fields to 'NA'. However, you should be aware of this when analyzing your data!")
        else:
            logger.info("No missing values encountered.")

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
                art_pubdate_day = "1"
            try:
                art_pubdate_month = pubdate_month[i + 1]
            except:
                art_pubdate_month = "1"
            try:
                art_pubdate_year = pubdate_year[i + 1]
            except:
                art_pubdate_year = "1900"
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
                   "source":"{} (print)".format(art_source2.lower()),
                   "text":art_text,
                   "section":art_section.lower(),
                   "byline":art_byline,
                   "datum":datetime.datetime(int(art_pubdate_year),int(art_pubdate_month),int(art_pubdate_day)),
                   }

            artnoemptykeys={k: v for k, v in art.items() if v}

            yield artnoemptykeys


