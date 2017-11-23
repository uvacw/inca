import os
import nltk
from nltk.corpus import stopwords
from gensim.utils import tokenize

stop_words = set(stopwords.words('english'))


def get_normalizer(norm_type):
    """
    Returns a lambda function that acts as a normalizer for input words/tokens.\n
    :param norm_type: the normalizer type to "construct". Recommended 'lemmatize'. If type is not in the allowed types then does not normalize (lambda just forwards the input to output as it is)
    :type norm_type: {'stem', 'lemmatize'}
    :return: the lambda callable object to perform normalization
    :rtype: lambda
    """
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
    """
    Given input text_data, a normalize 'command' and a stopwords filtering flag, generates a normalized, lowercased word/token provided that it passes the filter and that its length is bigger than 2 characters.\n
    :param text_data: the text from which to generate (i.e. doc['text'])
    :type text_data: str
    :param normalize: the type of normalization to perform. Recommended 'lemmatize'
    :type normalize: {'stem', 'lemmatize'}, else does not normalize
    :param word_filter: switch/flag to control stopwords filtering
    :type word_filter: boolean
    :return: the generated word/token
    :rtype: str
    """
    normalizer = get_normalizer(normalize)
    for word in (_.lower() for _ in tokenize(text_data)):
        if word_filter and (word in stop_words or len(word) < 3):
            continue
        yield normalizer(word)


def extract_data(document, field='text'):
    """
    Extracts data from the input document, given a field of interest.\n
    :param document: the dictionary to extract data from
    :type document: dict
    :param field: the requested dictionary key pointing to the dict data. If 'all' is given then returns the concatenation of all the dictionary values with '\\\\n'
    :type field: str
    :return: the requested textual data if key is found or if key == 'all'. Else returns None
    :rtype: str
    """
    if field in document:
        return document[field]
    elif field == 'all':
        return '\n'.join((text_data for text_data in document.values()))
    else:
        return None

def get_data_generator(documents, field='text'):
    """
    Returns a generator that can be iterated to extract textual data per document, according to the given field key.\n
    :param documents: the input dictionaries to generate from
    :type documents: iterable
    :param field: the key specifying the data to extract from the documents. If 'all' is given then returns the concatenation of all the dictionary values with '\\\\n'
    :type field: str
    :return: a generator of textual data
    :rtype: generator
    """
    return (extract_data(doc, field=field) for doc in documents)


def dir2docs(dir):
    """
    Given a directory (relative or absolute path) containing files, returns a list of dictionaries (one per file found in the directory) with a single 'text' key holding the read content. Can be used for creating "small" train/test datasets for testing purposes.\n
    :param dir: the path pointing to the directory
    :type dir: str
    :return: the dictionaries created
    :rtype: list
    """
    docs_list = os.listdir(dir)
    root_dir = os.path.dirname(dir)
    docs = []
    for text_file in docs_list:
        with open(root_dir + '/' + dir + '/' + text_file, 'r') as f:
            docs.append({'text': f.read()})
    return docs
