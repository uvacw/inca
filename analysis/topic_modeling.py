#!/usr/bin/env python3

import re
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

root_dir = os.path.dirname(os.path.realpath(__file__))


def create_corpus(documents, field='text', normalizing='lemmatize'):
    """
    :param documents: an iterable of documents (dictionaries)
    :param field: the field from which to extract data
    :param normalizing: if 'lemmatize' then perfoms word net lemmatization with the default pos noun ('n')
                        if 'stem' perform stemming with the porter stemmer
                        else uses the input words as they are.
    """
    print('Creating corpus ...')
    print('caching token represetation from documents ...')
    token_lists = [[word for word in generate_word(doc_data, normalize=normalizing)] for doc_data in get_data_generator(documents, field=field)]

    ddict = Dictionary(token_lists)
    corpus = [ddict.doc2bow(token_list) for token_list in token_lists]
    gensim.corpora.MmCorpus.serialize('/tmp/lda.mm', corpus)

    return ddict, corpus


class Lda(Analysis):

    def __init__(self):
        self.times_fitted = 0
        self.corpus = None
        self.ddict = None
        self.lda = None
        self.nb_docs_trained = 0
        self.selected_clusters = set()

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
        self.ddict, self.corpus = create_corpus(documents, field=field, normalizing='lemmatize')
        print('Training Lda model ...')
        self.lda = LdaModel(corpus=self.corpus, num_topics=nb_topics, alpha='auto')  # alpha can be also set to 'symmetric' or to an explicit array
        self.nb_docs_trained = len(self.corpus)
        #lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100, update_every=0, passes=20)

    def predict(self, documents, add_prediction='', field='text'):
        docs_lda = []
        for doc in documents:
            docs_lda.append(self.lda[get_bow(extract_data(doc, field=field), self.corpus)])
            if add_prediction != '':
                doc[add_prediction] = str(docs_lda[-1])

    def update(self, documents, field='text'):
        pass
        # corp = CorpusCreator.create_corpus(documents, field=field, normalizing=self.corpus.normalizer)
        # print('Updating model ...')
        # self.lda.update((get_bow(text_data, corp) for text_data in get_data_generator(documents, field=field)))

    # def interpretation(self):
    #     ordered_selected_clusters = [_id for _id in range(self.lda.num_topics) if _id in self.selected_clusters]
    #     top_words = []
    #     for idd in ordered_selected_clusters:
    #         top_words.append(self.lda.show_topic(idd))

    #     b = ''
    #     b = str(self.lda.print_topics())
    #     probs = re.findall(r'(\d\.\d+)\*', b)
    #     id_list = re.findall(r'\"(\d+)\"', b)
    #     o = ''
    #     for cl in range(t):
    #         o += '{}: [{}]\n'.format(cl, ' + '.join(map(lambda x: '{}*"{}"'.format(x[0], self.ddict[int(x[1])]), zip(probs[cl*10:cl*10+10], id_list[cl*10:cl*10+10]))))
    #     return o

    # def _gen_row(top, prob_precision=3):
    #     print(type(top))
    #     max_token_len = max(len(self.ddict[int(top[j][i][0])]) for j in range(len(top)) for i in range(len(top[0])))
    #     print('max: {}'.format(max_token_len))
    #     for i in range(len(top[0])):
    #         print(' |'.join('{}*'.format(str(self.ddict[int(top[j][i][0])]) + ' '*(max_token_len-len(self.ddict[int(top[j][i][0])]))) + "{1:.{0}f}".format(prob_precision, top[j][i][1]) for j in range(len(top))))

    def gen_row(self, top, prob_precision=3):
        max_token_len = max(len(self.ddict[int(top[j][i][0])]) for j in range(len(top)) for i in range(len(top[0])))
        print('max: {}'.format(max_token_len))
        for i in range(len(top[0])):
            print(' |'.join('{}*'.format(str(self.ddict[int(top[j][i][0])]) + ' '*(max_token_len-len(self.ddict[int(top[j][i][0])]))) + "{1:.{0}f}".format(prob_precision, top[j][i][1]) for j in range(len(top))))


    def select_topics(self, topic_ids):
        """Use this method to indicate which topics/clusters you are interested in for "selecting" (i.e. interpreting, visualizing) by providing your desired numerical ids. Note that it only adds to the set of currently "selected" topics the new ids provided. To clear the set before selecting use "clear_selected_topics" first.\n
        :param topic_ids: the numerical ids of the topics/clusters to add to the "selected" set
        :type topic_ids: list
        """
        self.selected_clusters.update(topic_ids)

    def deselect_topics(self, topic_ids):
        """Use this method to indicate which topics/clusters you are NOT interested in "selecting" (i.e. for interpreting, visualizing..) by providing your desired numerical ids to exclude from the selected set. It removes the found ids from the set.\n
        :param topic_ids: the numerical ids of the topics/clusters to remove from the "selected" set
        :type topic_ids: list
        """
        self.selected_clusters.difference_update(topic_ids)

    def select_all_topics(self):
        """Use this method in case you are want to "select" (i.e. for interpreting, visualizing..) all topics/clusters infered by the model. It adds all numerical topic/cluster ids to the "selected" set."""
        self.selected_clusters.update(range(self.lda.num_topics))

    def clear_selected_topics(self):
        """Use this method to clear the selection of topics/clusters. It removes all nnumerical ids from the "selected" set"""
        self.selected_clusters.clear()


def get_bow(text_data, corpus):
    return corpus.dict_obj.doc2bow([w for w in generate_word(text_data, normalize=corpus.normalizer)])


if __name__ == '__main__':
    print('')
    train_dir = sys.argv[1]
    test_dir = sys.argv[2]

    train_docs = dir2docs(train_dir)
    test_docs = dir2docs(test_dir)

#    ddict, corp = create_corpus(train_docs, field='text', normalizing='lemmatize')

 #   print('Corpus initialized. Number of docs included: {}'.format(len(corp)))
  #  print('Dicttionary initialized. Number of terms included: {}'.format(len(ddict)))

    l = Lda()
    l.fit(train_docs, nb_topics=2)

    # b = l.interpretation()
    # print(b)

    # for t in test_docs:
    #     lda.get_topic_distribution(t)
