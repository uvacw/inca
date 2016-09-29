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

SPEACH_VERBS = ['accepteer','antwoord','beaam','bedenk','bedoel','begrijp','beken','beklemtoon',
                'bekrachtig','belijd','beluister','benadruk','bereken','bericht','beschouw',
                'beschrijf','besef','betuig','bevestig','bevroed','beweer','bewijs','bezweer',
                'biecht','breng','brul','concludeer','confirmeer','constateer','debiteer',
                'declareer','demonstreer','denk','draag_uit','email','erken','expliceer',
                'expliciteer','fantaseer','formuleer','geef_aan','geloof','hoor','hamer',
                'herinner','houd_vol','kondig_aan','kwetter','licht_toe','maak_bekend',
                'maak_hard','meld','merk','merk_op','motiveer','noem','nuanceer','observeer',
                'onderschrijf','onderstreep','onthul','ontsluier','ontval','ontvouw','oordeel',
                'parafraseer','pos- tuleer','preciseer','presumeer','pretendeer','publiceer',
                'rapporteer','realiseer','redeneer','refereer','reken','roep','roer_aan',
                'ruik','schat','schets','schilder','schreeuw','schrijf','signaleer','snap',
                'snater','specificeer','spreek_uit','staaf','stel','stip_aan','suggereer',
                'tater','teken_aan','toon_aan','twitter','verbaas','verhaal','verklaar',
                'verklap','verkondig','vermoed','veronderstel','verraad','vertel','vertel_na',
                'verwacht','verwittig','verwonder','verzeker','vind','voel','voel_aan',
                'waarschuw','wed','weet','wijs_aan','wind','zeg','zet_uiteen','zie','twitter']

class alpino_to_quote(Processer):
    '''Takes alpino output and extracts quotes'''

    def process(self, alpino_result):
        '''takes an alpino result and returns a list of {speaker:name,using:verb,quote:text} dicts'''

        quotes = []
        for num,line in enumerate(alpino_result):
            mapped, tokens = map_parse(line)
            line_quotes= []
            line_quotes.extend(type_a(mapped,tokens))
            line_quotes.extend(type_b(mapped, tokens))
            line_quotes.extend(type_c(mapped, tokens))
            line_quotes.extend(type_d(mapped, tokens))
            line_quotes.extend(type_e(mapped, tokens))
        return quotes

# map dependency & token list
def map_parse(alpino_parse):
    if not alpino_parse.get('tokens',[]): return pandas.DataFrame(), pandas.DataFrame()
    tokens       = pandas.DataFrame(alpino_parse['tokens'])
    dependencies = pandas.DataFrame(alpino_parse['dependencies'])
    mapped = dependencies.merge(tokens[['id','lemma']], left_on='child', right_on='id', suffixes=('','lemma'))
    mapped.columns = ['child','parent','relation','child_id','child_lemma']
    mapped = mapped.merge(tokens[['id','lemma']], left_on='parent', right_on='id', suffixes=('','lemma'))
    mapped.columns = ['child', 'parent', 'relation', 'child_id','child_lemma','parent_id', 'parent_lemma']
    return mapped, tokens

# relational parser
def get_relation(mapped, child=True, relation=True, parent=True):
    id_type = lambda x: type(x)!=str
    if id_type(child):
        child_condition = type(child) == bool and (True) or (mapped.child_id ==int(child))
    else:
        child_condition    = type(child)  == bool and True or (mapped.child_lemma==child)

    relation_condition = type(relation)     == bool and True or (mapped.relation==relation)

    if id_type(parent):
        parent_condition = type(parent) == bool and (True) or (mapped.parent_id == int(parent))
    else:
        parent_condition   = type(parent) == bool and True or (mapped.parent_lemma==parent)

    return mapped[ (mapped.child==mapped.child) & child_condition & relation_condition & parent_condition]

def get_literal(tokens):
    r = re.compile(r'[\'"“”„]|,{2,2}')
    start = min(tokens.offset[[r.search(w)!=None for w in tokens.word]],default=-1)
    end   = max(tokens.offset[[r.search(w)!=None for w in tokens.word]],default=-1)
    if start!=-1 and end!=-1 and start!=end:
        return list(tokens.id[tokens.offset.isin(list(range(start,end+1)))])
    else:
        return []

def get_series(tokens, start=0, end=False):
    if not end:
        end = max(tokens.offset)
    return ' '.join(tokens.sort_values('offset')[(tokens.offset>=start)&(tokens.offset<=end)].word)

def get_list(tokens, indices, pos_major=''):
    return tokens[tokens.id.isin(indices)].sort('offset').word

def tracer(wordid, direction="up", prev=[]):
    trace = []
    if direction=="up":
        parent = get_relation(mapped, child=wordid).parent.values
    else:
        parent = get_relation(mapped, parent=wordid).child.values
    if parent.any():
        trace.extend([p for p in parent])
        [trace.extend(tracer(p, direction,prev=trace+prev)) for p in parent if p not in prev]
    return trace

# extract relations where necessary
def get_source(verb_id):
    subject = tokens[tokens.id.isin(get_relation(mapped, relation='su', parent=verb_id).child)]
    if subject.empty:
        return ''
    elif subject.lemma.values[0]=='en':
        return ';'.join(get_list(tokens, tracer(subject.id,'down')))
    else:
        return ''.join(subject.word)

def type_c(mapped,tokens):
    if mapped.empty or tokens.empty: return []
    verbs = tokens[tokens.lemma.isin(SPEACH_VERBS)]
    quotes = []
    for verb_id in verbs.id:
        type_c_relation    = get_relation(mapped, child='dat',relation='vc',parent=verb_id)
        if type_c_relation.empty:
            type_c_2_relation  = get_relation(mapped, child='hoop', relation='obj1', parent=verb_id)
            if type_c_2_relation.empty: continue
            type_c_2b_relation = get_relation(mapped, child='dat', relation='vc', parent=type_c_2_relation.child)
            if type_c_2b_relation.empty:continue
            body = get_list(tokens,tracer(type_c_2b_relation.child,'down'))
        else:
            body = get_list(tokens, tracer(type_c_relation.child, 'down'))
        verb_word  = tokens[tokens.id==verb_id].word.values[0]
        verb_lemma = tokens[tokens.id==verb_id].lemma.values[0]
        source = get_source(verb_id)
        quotes.append({
            'type':'C',
            'literal':'no',
            'verb_lemma': verb_lemma,
            'verb_word': verb_word,
            'source':source,
            'body':' '.join(body)
        })
    return quotes

def type_a(mapped, tokens):
    if tokens.empty or mapped.empty: return []
    quotes = []
    verbs = tokens[tokens.lemma=="blijk"]
    if verbs.empty: return []
    type_a_relation = get_relation(mapped, child='uit', relation='pc', parent=verbs.id.values[0])
    if type_a_relation.empty: return []
    source = ' '.join(get_list(tokens,tracer(type_a_relation.child.values[0],'down')))
    type_a_body_relation = get_relation(mapped, relation='su', parent=verbs.id.values[0])
    if type_a_body_relation.empty:
        body = ""
    else:
        body  = get_list(tokens, tracer(type_a_body_relation.child,'down'))
        if body.empty:
            body = ''
            pass #Should solve for 'dat' reference
        else:
            body = ' '.join(body)
    quotes.append({
        'type':'A',
        'literal':'no',
        'verb_lemma':'blijk',
        'verb_word':verbs.word.values[0],
        'source':source,
        'body':body
    })
    return quotes

def pivot(mapped, series):
    pivot = set()
    for element in series:
        if not pivot:
            pivot = set(tracer(element,'up'))
        else:
            pivot = pivot.intersection(set(tracer(element,'up')))
    return pivot

def type_b(mapped,tokens):
    if mapped.empty or tokens.empty: return []
    accordings = tokens[tokens.lemma.isin(['volgens','aldus'])]
    if accordings.empty: return []
    quotes = []
    for acc in accordings.id:
        type_b_quote_relation = pandas.concat([get_relation(mapped, relation="tag",child=acc),
                                              get_relation(mapped, relation="mod", child=acc)])
        source_ids = tracer(acc,'down')
        pivot = set(tracer(acc,'up')).intersection(set(tracer(type_b_quote_relation.parent,'up')))
        quote_ids  = [id for id in tracer(min(pivot),'down') if
                      id not in source_ids + [acc]]
        quotes.append({
            'type':'B',
            'literal':'no',
            'verb_lemma':tokens.lemma[tokens.id==acc].values[0],
            'verb_word': tokens.word[tokens.id == acc].values[0],
            'source':' '.join(get_list(tokens,source_ids)),
            'body':' '.join(get_list(tokens,quote_ids))
        })
    return quotes

def type_d(mapped, tokens):
    literal = get_literal(tokens)
    if literal:
        name = tokens.word[(tokens.pos=='name')&(tokens.id.isin(literal)==False)]
        pron = tokens.word[(tokens.pos=='pron')&(tokens.id.isin(literal)==False)]

        verb = tokens[(tokens.lemma.isin(SPEACH_VERBS))&(tokens.id.isin(literal)==False)]

        if not name.empty:
            source = ' '.join(name)
        else:
            source = ' '.join(pron)
        return [{
            'type':'D',
            'literal':'yes',
            'verb_lemma':' '.join(verb.lemma),
            'verb_word':' '.join(verb.word),
            'source':source,
            'body':' '.join(get_list(tokens,literal))
        }]
    else:
        return []

def type_e(mapped,tokens):
    quotes = []
    verbs = tokens[(tokens.lemma.isin(SPEACH_VERBS))&(tokens.pos=='verb')]
    for token in verbs.id:
        verb = tokens[(tokens.lemma.isin(SPEACH_VERBS)) & (tokens.id.isin(literal) == False)]

        verb_sub = get_relation(mapped, relation='su', parent=token)
        verb_source = tracer(verb_sub.child,'down') + list(verb_sub.child)

        verb_obj = get_relation(mapped, relation='obj1', parent=token)
        verb_body = tracer(verb_obj.child,'down')+list(verb_obj.child)

        quotes.append({
            'type':'E',
            'literal':'no',
            'verb_lemma': ' '.join(verb.lemma),
            'verb_word':' '.join(verb.word),
            'source': ' '.join(get_list(tokens,verb_source)),
            'body': ' '.join(get_list(tokens, verb_body))
        })
    return quotes