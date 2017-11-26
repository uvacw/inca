#!/usr/bin/env python3

import os
import sys
import nltk
import gensim
from nltk.corpus import stopwords
from gensim.utils import tokenize
from gensim.models.ldamodel import LdaModel
from core.analysis_base_class import Analysis
from gensim.corpora.dictionary import Dictionary
from helpers.text_preprocessing import *
# from helpers.text_preprocessing import generate_word
# from helpers.text_preprocessing import dir2docs

root_dir = os.path.dirname(os.path.realpath(__file__))


class CorpusCreator:
    @staticmethod
    def create_corpus(documents, field='text', normalizing='lemmatize'):
        """
        :param documents: an iterable of documents (dictionaries)
        :param field: the field from which to extract data
        :param normalizing: if 'lemmatize' then perfoms word net lemmatization with the default pos noun ('n')
                            if 'stem' perform stemming with the porter stemmer
                            else uses the input words as they are.
        """
        print('Creating corpus ...')
        corpus = Corpus(normalizing)
        for doc in documents:
            corpus.add_doc(doc, field='text')
        return corpus

class Corpus:

    def __init__(self, normalizer):
        self.normalizer = normalizer
        self.id2doc = {}  # int => str
        self.doc2id = {}  # str => int
        self.next_doc_id = 0
        self.dict_obj = Dictionary()

    def add_doc(self, document, field='text'):
        self.id2doc[self.next_doc_id] = extract_data(document, field=field)
        self.doc2id[extract_data(document, field=field)] = self.next_doc_id
        token_list = [word for word in generate_word(extract_data(document, field=field), normalize=self.normalizer)]
        self.dict_obj.add_documents([token_list])
        self.next_doc_id += 1

    def __len__(self):
        return self.next_doc_id

class Lda(Analysis):

    def __init__(self, corpus):
        self.corpus = corpus
        self.times_fitted = 0
        self.lda = None

        self.nb_docs_trained = 0

    def fit(self, documents, add_prediction='', field='text', nb_topics=20, **kwargs):
        """
        This method trains the Lda model by fitting its parameters to the extracted textual data from the given documents\
        (dictionaries) and selected field key. It infers n number of topics/clusters equal to the given parameter.\
        Input documents can be optionally mutated by adding to them the trained model "prediction" value.\n

        `alpha` and `eta` are hyperparameters that affect sparsity of the document-topic (theta) and topic-word (lambda)\
         distributions respectively. 'alpha' parameter is learned as an asymmetric prior directly from your data and 'eta'\
         defaults to a symmetric 1.0/nb_topics prior.\n

        `decay` and `offset` parameters are the same as Kappa and Tau_0 in Hoffman et al, respectively.\n\n

        :param documents: the documents (dictionaries) to train on
        :type documents: iterable
        :param add_prediction: this switch signals the mutation of the train set documents by adding a key, value pair,\
            per document. The value holds the documents's topic distribution predicted by the trained model
        :param field: the requested dictionary/document key pointing to the data. If 'all' is given then returns the\
            concatenation of all the dictionary values with '\\\\n'
        :type field: str
        :param nb_topics: the number of clusters/topics to assume when performing topic modeling. Controls granularity
        :type nb_topics: int

        :References:
        * https://radimrehurek.com/gensim/models/ldamodel.html : gensim.models.ldamodel
        * https://www.di.ens.fr/~fbach/mdhnips2010.pdf : Hoffman et al
        """
        print('Training Lda model ...')
        cached = (get_bow(text_data, self.corpus) for text_data in get_data_generator(documents, field=field))
        self.lda = LdaModel(cached, num_topics=nb_topics, alpha='auto')  # alpha can be also set to 'symmetric' or to an explicit array
        self.nb_docs_trained = len(self.corpus)
        #lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100, update_every=0, passes=20)

    def predict(self, documents, add_prediction='', field='text'):
        docs_lda = []
        for doc in documents:
            docs_lda.append(self.lda[get_bow(extract_data(doc, field=field), self.corpus)])
            if add_prediction != '':
                doc[add_prediction] = str(docs_lda[-1])

    def update(self, documents, field='text'):
        corp = CorpusCreator.create_corpus(documents, field=field, normalizing=self.corpus.normalizer)
        print('Updating model ...')
        self.lda.update((get_bow(text_data, corp) for text_data in get_data_generator(documents, field=field)))

    def interpretation(self):
        return self.lda.print_topics(num_topics=-1, num_words=10)

    # def quality(self):

    # def get_topic_distribution(self, new_doc, field='text'):  # predict/infer
    #     # self._corpus.add_doc(new_doc, field='text')
    #     self.lda[get_bow(new_doc[field], self.corpus)]


class TopicModelTrainer:

    def __init__(self, corpus):
        self.corpus = corpus

    def train(self, model_type, train_docs, field='text', nb_topics=20):
        """
        :param model_type: the model to use for inducing topics
        :type model_type: str
        :param train_docs: an iterable of dictionaries; the set of documents to train on
        :type train_docs: iterable
        :param field: the docs field from which to extract data
        :type field: str
        :param nb_topics: the assumed number of underlying topics
        :type nb_topics: int
        """
        if model_type == 'lda':
            model = Lda(self.corpus)
            model.fit(train_docs, add_prediction='', field=field, nb_topics=nb_topics)
#            model.fit([get_bow(extract_data(doc, field), self.corpus) for doc in train_docs], nb_topics)
        else:
            raise Exception("Topic model of type '{}' is not supported".format(model_type))
        return model

def get_bow(text_data, corpus):
    return corpus.dict_obj.doc2bow([w for w in generate_word(text_data, normalize=corpus.normalizer)])


if __name__ == '__main__':
    print('')
    train_dir = sys.argv[1]
    test_dir = sys.argv[2]

    train_docs = dir2docs(train_dir)
    test_docs = dir2docs(test_dir)

    corp = CorpusCreator.create_corpus(train_docs, field='text', normalizing='lemmatize')

    print('Corpus initialized. Number of documents included: {}'.format(len(corp)))

    trainer = TopicModelTrainer(corp)
    lda = trainer.train('lda', train_docs, field='text', nb_topics=2)

    # for t in test_docs:
    #     lda.get_topic_distribution(t)
