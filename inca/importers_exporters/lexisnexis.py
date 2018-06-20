"""INCA Lexis Nexis import functionality

This file contains the input/output functionality for Lexis Nexis files

"""

from ..core.import_export_classes import Importer, Exporter
from ..core.basic_utils import dotkeys
import csv
import chardet
import logging
from os import listdir, walk
from os.path import isfile, join, splitext
import re
import datetime

logger = logging.getLogger("INCA."+__name__)


def _detect_encoding(filename):
    with open(filename, mode='rb') as filebuf:
        encoding = chardet.detect(filebuf.peek(10000000))
    return encoding['encoding']


def _detect_has_header(filename,encoding):
    with open(filename, mode='r', encoding=encoding) as fi:
        while True:
            line=next(fi)
            if line.strip().startswith('Download Request'):
                return True
            if line.strip().startswith('1 of'):
                return False

def check_suspicious(text):
    '''checks whether an article is likely to be a real article
    or a table with, e.g., sports results or stock exchange rates'''
    
    ii=0
    jj=0
    for token in text.replace(",","").replace(".","").split():
        ii+=1
        if token.isdigit():
            jj+=1
    # if more than 16% of the tokens are numbers, then suspicious = True.
    suspicious = jj > .16 * ii
    return suspicious


class lnimporter(Importer):
    """Read Lexis Nexis files"""

    version = 0.2

    def run(self, path, *args, **kwargs):
        """uses the documents from the load method in batches """

        # this method is overwritten because in contrast to
        # other importers, we do not have a single doctype.
        # Each document can have a different one.
        for doc in self.load(path, *args,**kwargs):
            self._ingest(iterable=doc, doctype=doc['doctype'])
            self.processed += 1


    def load(self, path, *args, **kwargs):
        """Loads a txt files from Lexis Nexis into INCA

        Parameters
        ----
        path : string
            The file to load
        encoding ; string (optional)
            The encoding in which a file is, defaults to 'utf-8', but is also
            commonly 'UTF-16','ANSI','WINDOwS-1251'. 'autodetect' will attempt
            to infer encoding from file contents

        yields
        ---
        dict
            One dict per article

        """


        self.MONTHMAP={"January":1, "januari": 1, "February":2, "februari":2,"March":3,"maart":3,
                        "April":4, "april":4, "mei":5, "May":5, "June":6,"juni":6, "July":7, "juli":7,
                        "augustus": 8, "August":8,"september":9,"September":9, "oktober":10,"October":10,
                        "November":11,"november":11,"December":12,"december":12}
        self.SOURCENAMEMAP={'ad/algemeen dagblad (print)':'ad (print)',
                                'de telegraaf (print)': 'telegraaf (print)',
                                'de volkskrant (print)': 'volkskrant (print)',
                                'nrc handelsblad (print)': 'nrc (print)'}


        self.pathwithlnfiles = path


        allinputfiles = []
        for path, subFolders, files in walk(self.pathwithlnfiles):
            for f in files:
                if isfile(join(path, f)) and splitext(f)[1].lower() == ".txt" and not f.startswith('.'):
                    allinputfiles.append(join(path, f))

        try:
            assert len(allinputfiles)> 0
        except AssertionError:
            logger.error('There are no files to be process. Please use a valid, non-empty directory')
            return
        article = 0
        logger.debug(allinputfiles)
        for articlesfile in allinputfiles:
            logger.info("Now processing {}".format(articlesfile))
            encoding = kwargs.pop('encoding',False)
            if not encoding:
                encoding = _detect_encoding(articlesfile)
            with open(articlesfile, "r", encoding=encoding, errors="replace") as f:
                if _detect_has_header(articlesfile, encoding):
                    for skiplines in range(22):
                        next(f)
                i = 0
                for line in f:
                    i = i + 1
                    line = line.replace("\r", " ")
                    if line == "\n":
                        continue
                    matchObj = re.match(r"\s+(\d+) of (\d+) DOCUMENTS", line) # beginning of a new article
                    # dealing with different date notations
                    matchObj2 = re.match(r"\s+(\d{1,2}) (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december) (\d{4}) (maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)", line)
                    matchObj2a = re.match(r"\s+(\d{1,2}) ([jJ]anuari|[fF]ebruari|[mM]aart|[aA]pril|[mM]ei|[jJ]uni|[jJ]uli|[aA]ugustus|[sS]eptember|[Oo]ktober|[nN]ovember|[dD]ecember) (\d{4}).*", line)
                    matchObj3 = re.match(r"\s+(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}),? (\d{4})", line)
                    matchObj4 = re.match(r"\s+(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4}) (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", line)
                    matchObj4a = re.match(r"\s+(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4}).*", line)
                    
                    if matchObj:
                        # new article starts
                        if article > 0:
                            # yield article, but not before we processed the first one
                            formattedsource = "{} (print)".format(journal2.lower())
                            formattedsource = self.SOURCENAMEMAP.get(formattedsource, formattedsource) # rename source if necessary
                            # minimal fields to be returned. These really need to be present
                            art = {
                                "title":title.strip(),
                                "doctype": formattedsource,
                                "text":text,
                                "publication_date":datetime.datetime(int(pubdate_year),int(pubdate_month),int(pubdate_day)),
                                "suspicious":check_suspicious(text)
                                }
                            # add fields where it is okay if they are absent
                            if len(section)>0:
                                art["category"] = section.lower()
                            if len(byline)>0:
                                art["byline"] = byline

                            # print(art)
                            
                            yield art

                        article += 1
                        logger.info('Now processing article {}'.format(article))

                        istitle=True #to make sure that text before mentioning of SECTION is regarded as title, not as body
                        firstdate=True # flag to make sure that only the first time a date is mentioned it is regarded as _the_ date
                        text = ""
                        title = ""
                        byline = ""
                        section = ""
                        length = ""
                        loaddate = ""
                        language = ""
                        pubtype = ""
                        journal = ""
                        journal2=""
                        pubdate_day = ""
                        pubdate_month = ""
                        pubdate_year = ""
                        pubdate_dayofweek = ""
                        suspicious=True
                        
                        while True:
                            nextline=next(f)
                            if nextline.strip()!="":
                                journal2=nextline.strip()
                                break
                        continue
                    
                    if line.startswith("BYLINE"):
                        byline = line.replace("BYLINE: ", "").rstrip("\n")
                    elif line.startswith("SECTION"):
                        istitle=False # everything that follows will be main text rather than title if no other keyword is mentioned
                        section = line.replace("SECTION: ", "").rstrip("\n")
                    elif line.startswith("LENGTH"):
                        length = line.replace("LENGTH: ", "").rstrip("\n").rstrip(" woorden")
                    elif line.startswith("LOAD-DATE"):
                        loaddate = line.replace("LOAD-DATE: ", "").rstrip("\n")
                    elif matchObj2 and firstdate==True:
                        # print matchObj2.string
                        pubdate_day=matchObj2.group(1)
                        pubdate_month=str(self.MONTHMAP[matchObj2.group(2)])
                        pubdate_year=matchObj2.group(3)
                        pubdate_dayofweek=matchObj2.group(4)
                        firstdate=False
                    elif matchObj2a and firstdate==True:
                        # print matchObj2.string
                        pubdate_day=matchObj2a.group(1)
                        pubdate_month=str(self.MONTHMAP[matchObj2a.group(2).lower()])
                        pubdate_year=matchObj2a.group(3)
                        firstdate=False
                    elif matchObj3 and firstdate==True:
                        pubdate_day=matchObj3.group(2)
                        pubdate_month=str(self.MONTHMAP[matchObj3.group(1)])
                        pubdate_year=matchObj3.group(3)
                        pubdate_dayofweek="NA"
                        firstdate=False
                    elif matchObj4 and firstdate==True:
                        pubdate_day=matchObj4.group(1)
                        pubdate_month=str(self.MONTHMAP[matchObj4.group(2)])
                        pubdate_year=matchObj4.group(3)
                        pubdate_dayofweek=matchObj4.group(4)
                        firstdate=False
                    elif matchObj4a and firstdate==True:
                        pubdate_day=matchObj4a.group(1)
                        pubdate_month=str(self.MONTHMAP[matchObj4a.group(2)])
                        pubdate_year=matchObj4a.group(3)
                        firstdate=False

                    elif (matchObj2 or matchObj2a or matchObj3 or matchObj4 or matchObj4a) and firstdate==False:
                        # if there is a line starting with a date later in the article, treat it as normal text
                        text = text + " " + line.rstrip("\n")
                    elif line.startswith("LANGUAGE"):
                        language = line.replace("LANGUAGE: ", "").rstrip("\n")
                    elif line.startswith("PUBLICATION-TYPE"):
                        pubtype = line.replace("PUBLICATION-TYPE: ", "").rstrip("\n")
                    elif line.startswith("JOURNAL-CODE"):
                        journal = line.replace("JOURNAL-CODE: ", "").rstrip("\n")
                    elif line.lstrip().startswith("Copyright ") or line.lstrip().startswith("All Rights Reserved"):
                        pass
                    elif line.lstrip().startswith("AD/Algemeen Dagblad") or line.lstrip().startswith(
                            "De Telegraaf") or line.lstrip().startswith("Trouw") or line.lstrip().startswith(
                            "de Volkskrant") or line.lstrip().startswith("NRC Handelsblad") or line.lstrip().startswith(
                            "Metro") or line.lstrip().startswith("Spits"):
                        pass
                    else:
                        if istitle:
                            title = title + " " + line.rstrip("\n")
                        else:
                            text = text + " " + line.rstrip("\n")

        # yield the very last article of the whole set 
        formattedsource = "{} (print)".format(journal2.lower())
        formattedsource = self.SOURCENAMEMAP.get(formattedsource, formattedsource) # rename source if necessary
        # minimal fields to be returned. These really need to be present
        art = {
            "title":title.strip(),
            "doctype": formattedsource,
            "text":text,
            "publication_date":datetime.datetime(int(pubdate_year),int(pubdate_month),int(pubdate_day)),
            }
        # add fields where it is okay if they are absent
        if len(section)>0:
            art["category"] = section.lower()
        if len(byline)>0:
            art["byline"] = byline
        yield art
