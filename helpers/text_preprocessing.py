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

def dir2docs(dir):
    docs_list = os.listdir(dir)
    docs = []
    for text_file in docs_list:
        with open(root_dir + '/' + dir + '/' + text_file, 'r') as f:
            docs.append({'text': f.read()})
    return docs
