import os
import nltk
from nltk.corpus import stopwords
from gensim.utils import tokenize

stop_words = set(stopwords.words('english'))


def get_normalizer(norm_type):
    if norm_type == 'stem':
        from nltk.stem import PorterStemmer
        stemmer = PorterStemmer()
        return lambda x: stemmer.stem(x)
    elif norm_type == 'lemmatize':
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        return lambda x: lemmatizer.lemmatize(x)
    else:
        return lambda x: x

def generate_word(text_data, normalize='lemmatize', word_filter=False):
    normalizer = get_normalizer(normalize)
    for word in (_.lower() for _ in tokenize(text_data)):
        if word_filter and (word in stop_words or len(word) < 3):
            continue
        yield normalizer(word)


def extract_data(document, field='text'):
    """
    Extracts data from the input document, given a field of interest.\n
    @param document: the document to extract data from
    @type document: dictionary
    @param field: the requested dictionary key pointing to the dict data. If 'all' is given then return the  concatenation of all the dictionaries values with '\n'. If key is not found returns empty string ''
    @type field: str
     """
    if field in document:
        return document[field]
    elif field == 'all':
        return '\n'.join((text_data for text_data in document.values()))
    else:
        return ''


def dir2docs(dir):
    docs_list = os.listdir(dir)
    docs = []
    for text_file in docs_list:
        with open(root_dir + '/' + dir + '/' + text_file, 'r') as f:
            docs.append({'text': f.read()})
    return docs
