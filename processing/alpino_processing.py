'''
Provides ALpino parsing functionality based on the XTAS implementation.
'''

from core.processor_class import Processer
from cytoolz import identity, pipe
import subprocess
import os
import datetime
import re
import configparser
import sys
import logging

logger = logging.getLogger(__name__)

if sys.version_info.major==2:
    logger.info("Detected python2 environment, using subprocess32 for timeout support")
    import subprocess32 as subprocess

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))

CMD_PARSE    = ["bin/Alpino", "end_hook=dependencies", "-parse"]
CMD_TOKENIZE = ["Tokenization/tok"]
ALPINO_HOME  = config.get("alpino", "alpino.home")
os.environ['ALPINO_HOME'] = os.path.join(os.getcwd(),ALPINO_HOME)

class alpino(Processer):
    def process(self, document_field, splitlines=True):
        """Alpino based tokenization and dependency parsing of Dutch texts"""
        if splitlines:
            document_field = re.split(r"[(\r\n).?!\n\\|]", document_field)
        else:
            document_field = [document_field]

        line_parses = []
        for line in document_field:
            line = encode_or_drop(line)
            if not line: continue # skip emtpy lines that may result from repeated delimitters
            p = subprocess.Popen(["bin/Alpino","end_hook=dependencies","-parse"],
                                 shell=False,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=os.environ['ALPINO_HOME'])
            try:
                parsed = p.communicate(line, timeout=int(config.get('alpino','alpino.timeout')))

            except subprocess.TimeoutExpired:
                logger.info("timeout trying to parse line, retrying once")
                try:
                    p.terminate()
                    p = subprocess.Popen(["bin/Alpino", "end_hook=dependencies", "-parse"],
                                         shell=False,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         cwd=os.environ['ALPINO_HOME'])
                    parsed = p.communicate(line, timeout=int(config.get('alpino', 'alpino.timeout')))
                except:
                    p.terminate()
                    line_parses.append({})
            except Exception as e:
                p.terminate()
                raise e
            p.terminate()
            tree   = interpret_parse(parsed[0])
            line_parses.append(tree)
        return line_parses

    def _test_function(self):
        '''tests whether alpino works'''
        try:
            self.process("de kat krabt de krullen")
            return {self.__name__ : {'status':True, 'message':'Alpino is available and working' }}
        except:
            return {self.__name__ : {'status':False, 'message':'Alpino is unavailable' }}

def encode_or_drop(line):
    safeline = []
    for char in line:
        try:
            char.encode('utf-8', 'replace')
            safeline.append(char)
        except: pass
    return ''.join(safeline).encode('utf-8','replace')

def _output_func(output, saf_func):
    try:
        return {"raw": identity, "saf": saf_func}[output]
    except KeyError:
        raise ValueError("Unknown output format %r" % output)

def parse_text(text):
    tokens = tokenize(text)
    parse = parse_raw(tokens)
    return interpret_parse(parse)


def tokenize(text):
    """
    Tokenize the given text using the alpino tokenizer.
    Input text should be a single unicode or utf-8 encoded string
    Returns a single utf-8 encoded string ready for Alpino,
    with spaces separating tokens and newlines sentences
    """
    alpino_home = os.environ['ALPINO_HOME']
    text = text.encode("utf-8")

    p = subprocess.Popen(CMD_TOKENIZE, shell=False, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=alpino_home)
    tokens, err = p.communicate(text)
    if 'error' in err or not tokens:
        raise Exception("Tokenization problem. Output was {tokens!r}, "
                        "error messages: {err!r}".format(**locals()))
    tokens = tokens.replace("|", "")  # alpino uses | for  'sid | line'
    return tokens


def parse_raw(tokens):
    alpino_home = os.environ['ALPINO_HOME']
    p = subprocess.Popen(CMD_PARSE, shell=False,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         cwd=alpino_home, env={'ALPINO_HOME': alpino_home})
    parse, err = p.communicate(tokens)
    if not parse:
        raise Exception("Parse problem. Output was {parse!r}, "
                        "error messages: {err!r}".format(**locals()))
    return parse


def interpret_parse(parse):
    module = {'module': "alpino",
              "started": datetime.datetime.now().isoformat()}
    header = {"header": {'format': "SAF",
                         'format-version': "0.0",
                         'processed': [module]
                         }}
    tokens = {}  # {(sid, offset): token}

    def get_token(sid, token_tuple):
        t = interpret_token(*token_tuple)
        if (sid, t['offset']) in tokens:
            return tokens[sid, t['offset']]
        else:
            tokens[sid, t['offset']] = t
            t['sentence'] = sid
            t['id'] = len(tokens)
            return t

    def get_deps(lines):
        for line in lines:
            # At some point, Alpino's dependencies end_hook started producing
            # "top" nodes, which we don't want in our output.
            if not line or line[0] == 'top':
                continue

            assert len(line) == 16
            sid = int(line[-1])
            parent = get_token(sid, line[:7])
            child = get_token(sid, line[8:15])
            func, rel = line[7].split("/")
            yield dict(child=child['id'], parent=parent['id'], relation=rel)


    lines = (line.decode("utf-8","ignore").strip().split("|")
             for line in parse.splitlines())
    dependencies = list(get_deps(lines))

    return dict(header=header, dependencies=dependencies,
                tokens=list(tokens.values()))


def interpret_token(lemma, word, begin, _end, major_pos, _pos2, pos):
    "Convert raw alpino token into a 'saf' dict"

    # Turn POS tags like "[stype=declarative]:verb" into just "verb" to
    # simulate the behavior of older Alpinos.
    pos = re.sub(r'^\[[^]]*\]:', '', pos)

    if pos == "denk_ik":  # is this a bug or a feature?
        major, minor = "verb", None
    elif "(" in pos:
        major, minor = pos.split("(", 1)
        minor = minor[:-1]
    else:
        major, minor = pos, None

    if "_" in major:
        m2 = major.split("_")[-1]
    else:
        m2 = major
    cat = _POSMAP.get(m2)
    if not cat:
        raise Exception("Unknown POS: %r (%s/%s/%s/%s)"
                        % (m2, major, begin, word, pos))

    return dict(word=word, lemma=lemma, pos=major_pos,
                offset=int(begin), pos_major=major,
                pos_minor=minor, pos1=cat)


_POSMAP = {"pronoun": 'O',
           "verb": 'V',
           "noun": 'N',
           "preposition": 'P',
           "determiner": "D",
           "comparative": "C",
           "adverb": "B",
           'adv': 'B',
           "adjective": "A",
           "complementizer": "C",
           "punct": ".",
           "conj": "C",
           "tag": "?",
           "particle": "R",
           "name": "M",
           "part": "R",
           "intensifier": "B",
           "number": "Q",
           "cat": "Q",
           "n": "Q",
           "reflexive": 'O',
           "conjunct": 'C',
           "pp": 'P',
           'anders': '?',
           'etc': '?',
           'enumeration': '?',
           'np': 'N',
           'p': 'P',
           'quant': 'Q',
           'sg': '?',
           'zo': '?',
           'max': '?',
           'mogelijk': '?',
           'sbar': '?',
           '--': '?',
           }
# drawn from  van Atteveldt, Sheaferm, Shenhav 2015: "Clause analysis: using syntactic information to enrich frequency-based automatic content analysis"
SPEACH_VERBS = ["accepteer", "antwoord", "beaam", "bedenk", "bedoel", "begrijp", "beken", "beklemtoon", "bekrachtig", "belijd", "beluister", "benadruk", "bereken", "bericht", "beschouw", "beschrijf", "besef", "betuig", "bevestig", "bevroed", "beweer", "bewijs", "bezweer", "biecht", "breng", "brul", "concludeer", "confirmeer", "constateer", "debiteer", "declareer", "demonstreer", "denk", "draag_uit", "email", "erken", "expliceer", "expliciteer", "fantaseer", "formuleer", "geef_aan", "geloof", "hoor", "hamer", "herinner", "houd_vol", "kondig_aan", "kwetter", "licht_toe", "maak_bekend", "maak_hard", "meld", "merk", "merk_op", "motiveer", "noem", "nuanceer", "observeer", "onderschrijf", "onderstreep", "onthul", "ontsluier", "ontval", "ontvouw", "oordeel", "parafraseer", "postuleer", "preciseer", "presumeer", "pretendeer", "publiceer", "rapporteer", "realiseer", "redeneer", "refereer", "reken", "roep", "roer_aan", "ruik", "schat", "schets", "schilder", "schreeuw", "schrijf", "signaleer", "snap", "snater", "specificeer", "spreek_uit", "staaf", "stel", "stip_aan", "suggereer", "tater", "teken_aan", "toon_aan", "twitter", "verbaas", "verhaal", "verklaar", "verklap", "verkondig", "vermoed", "veronderstel", "verraad", "vertel", "vertel_na", "verwacht", "verwittig", "verwonder", "verzeker", "vind", "voel", "voel_aan", "waarschuw", "wed", "weet", "wijs_aan", "wind", "zeg", "zet_uiteen", "zie", "twitter"]

class alpino_to_quote(Processer):
    '''Takes alpino output and extracts quotes'''

    def process(self, alpino_result):
        '''takes an alpino result and returns a list of {speaker:name,using:verb,quote:text} dicts'''

        quotes = []
        for num, line in enumerate(alpino_result):
            speach_verbs = [verb for verb in line.get('tokens',[]) if verb.get('lemma') in SPEACH_VERBS]
            if speach_verbs:
                speach_verbs = speach_verbs[0]
                subject_id = [dep.get('child') for dep in line.get('dependencies',[]) if
                              dep.get('relation')=='su' and dep.get('parent')==speach_verbs.get('id',False) ][0]
                verb    = speach_verbs.get('lemma','')

                def get_children(parent, exclude=False):
                    child_ids = [sub['child'] for sub in line.get('dependencies') if
                                 sub['parent']==parent and not sub['child']==exclude]
                    for child in child_ids:
                        child_ids.extend(get_children(child))
                    return child_ids

                def id_to_word(id):
                    return [sub['word'] for sub in line.get('tokens') if sub['id']==id][0]

                quote = ' '.join([id_to_word(child) for child in get_children(speach_verbs.get('id'), exclude=subject_id)])
                quotes.append({
                'speaker':id_to_word(subject_id),
                'verb':speach_verbs.get('word'),
                'quote':quote
                 })
        return quotes