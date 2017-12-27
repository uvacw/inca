import sys
import pattern
import pandas as pd
import inca
from inca import Inca
#from analysis_classification_class import classification
import core.search_utils


import logging
import numpy as np
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn import metrics
#from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.cross_validation import KFold
from core.analysis_base_class import Analysis
from scipy.sparse import csr_matrix
from sklearn.linear_model import SGDClassifier
import string

from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score

from elasticsearch import Elasticsearch
from datetime import datetime
es = Elasticsearch()

logger = logging.getLogger(__name__)

class classification(Analysis):
    
    def __init__(self):
        self.model = None
        self.vocab = None
        self.train_predictions = None
        self.X_test = None
        self.y_test = None
        self.predictions = None
        self.accuracy = None
        self.valid_docs = []
        self.invalid_docs = []
        self.vectorizer = None

        self.labels = []
        
        
    def fit(self, documents, x_field, label_field, doctype=None, add_prediction=False, testsize = 0.2, mindf = 0.0, maxdf = 1.0, rand_shuffle = True, tfidf = True, vocabul = None):
        """
        This method should train a Classifier model on the input documents.\n
        @param documents: the documents (stored in elasticsearch) to train on      
        @type documents: iterable           
        @param x_field: The nested field name that contains the text articles to be classified. Ideally nested within the '_source'
                        field. For instance, to use nested field x2 as text document which is nested as doc['_source']['x1']['x2'], use
                        '_source.x1.x2'
                        (Makes a function call to core.basic_search.utilsdotkeys(dict, key_string) : allows the use of .-separated
                        nested fields such as 'name.firstname' as dict[name][firstname])
        @type x_field: str
        @param label_field: The nested field name that contains the labels.Ideally would be nested within the '_source' field. For
                            instance, to use nested field x2 as label which is nested as doc['_source']['x1']['x2'], use '_source.x1.x2'
        @type label_field: str
        @param doctype: the ElasticSearch doctype provided to the set of documents
        @type doctype: str
        @param add_prediction: this switch signals whether it is desired to obtain the class predictions for the train examples using the model trained on the train set itself.\
                               If given (add_prediction == True), then the in-sample, i.e., the train example class predictions as predicted by the model are outputted:\n
        @type add_prediction: Boolean
        @param testsize: The proportion of labeled document examples to reserve as a test set. The default has been set as 0.2.
        @type testsize: float
        @param mindf: While creating the vocabulary (using a CountVectorizer from scikit), ignore all terms with a
                      document frequency (that is, the proportion of train documents in which the term was found) strictly lower 
                      than the threshold specified by mindf. The default has been set to 0.0.
        @type mindf: float
        @param maxdf: While creating the vocabulary (using a CountVectorizer from scikit), ignore all terms with a document
                      frequency (that is, the proportion of train documents in which the term was found) strictly higher than 
                      the threshold specified by maxdf. The default has been set to 1.0.
        @type maxdf: float
        @param rand_shuffle: If true, then the labeled document examples given as input, are randomly shuffled before splitting
                             into a test and train set. If set to False, then no randomising is performed before the test-train 
                             split. The Default is set to True.
        @type rand_shuffle: Boolean
        @param tfidf: If true, then the Classifier model is based on the term-frequency-inverse-document-frequency instead of 
                      merely the term frequency. That is, it weights the frequency counts of words found in each document with
                      the inverse document frequency (the number of documents that particuar word has occured.) The Default is 
                      set to True.
        @type tfidf: Boolean
        @param vocabul: This parameter accepts a list of words to be hard-fed as the vocabulary on basis of which the word 
                        frequency features are to be extracted from the input labeled documents. The default is set to None,
                        in which case, all tokenised terms above the 'mindf', and below the 'maxdf' thresholds (defined above)
                        encountered in the labeled documents are used to form the vocabulary.
        @type vocabul: list, or None type object
        
        
        
        """
        counter = 0
        invalidchars = set(string.punctuation)

        for doc in documents:
            counter+=1
            if len(core.basic_utils.dotkeys(doc, x_field))>0:
                self.valid_docs.append(doc['_id'])
                self.labels.append(core.basic_utils.dotkeys(doc, label_field))             

                if counter <5:
                    text = core.basic_utils.dotkeys(doc, x_field).lower()
                    if any(char in invalidchars for char in text):
                        logger.info('Punctuation has not been removed. Proceeding without pre-processing.')


            else: 
                self.invalid_docs.append(doc['_id'])
       
        documents = client.database.doctype_generator(doctype) 

        self.vectorizer = CountVectorizer(min_df = mindf, max_df = maxdf, vocabulary = vocabul) 
        counts = self.vectorizer.fit_transform((core.basic_utils.dotkeys(doc, x_field) for doc in documents if doc['_id'] not in self.invalid_docs), self.labels)

        self.vocab = np.array(self.vectorizer.get_feature_names())
           
    
        if tfidf:
            self.vectorizer = TfidfTransformer()        
            tfidf_full_data = self.vectorizer.fit_transform(counts, self.labels)
            X_train, self.X_test, y_train, self.y_test = train_test_split(tfidf_full_data, self.labels, test_size=testsize, shuffle = rand_shuffle, random_state=42)
        
        else:
            X_train, self.X_test, y_train, self.y_test = train_test_split(counts, self.labels, test_size = testsize, shuffle = rand_shuffle, random_state=42)
        
        self.model =  SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, max_iter=1000, random_state=42).fit(X_train, y_train)
        print(type(X_train), '\n', type(self.y_test))
        #If predictions for training documents are desired
        if add_prediction ==True:
            self.train_predictions = self.model.predict(X_train)
        else:
            self.train_predictions = None
                    
        return (self.vocab, counts, self.labels)

                                       
    def predict(self, documents = None, x_field=None, doctype = None,  **kwargs):
        """
        This method performs classification of new unseen documents.\n
        @param documents: the documents to classify.
        @type documents: iterable, or a scipy sparse csr matrix of features (representing term frequencies or tfidf values).
        @param x_field: The nested field name that contains the text articles to be classified. Ideally nested within the '_source'
                        field. For instance, to use nested field x2 as text document which is nested as doc['_source']['x1']['x2'], use
                        '_source.x1.x2'
                        (Makes a function call to core.basic_search.utilsdotkeys(dict, key_string) : allows the use of .-separated
                        nested fields such as 'name.firstname' as dict[name][firstname])
        @type x_field: str
        @param doctype: the ElasticSearch doctype provided to the set of documents
        @type doctype: str        
        """
        
        if documents == None:
            documents = self.X_test
        else:
            documents = self.vectorizer.transform(documents)
          
        
        print(type(self.X_test))
        self.predictions = self.model.predict(documents)
        print('no_of predictions : ',len(self.predictions))
                                                                
        return (self.predictions)
                                                 
                                                   
 
    def quality(self, **kwargs):
        """
        This method has the functionality to report on the quality of the underlying Classification (trained) model which was created as a random subset as a proportion of the input documents.\n
        The size of the test set is controlled through the parameter 'testsize' of the fit method of the Classification analyser object. The default proportion is 0.2, with random shuffle set as True.\n
        It calculates the categorization accuracy, precision, recall and f1-score on the test set of examples.\n

        """
        #make the test predictions as an attribute.

        test_pred = self.model.predict(self.X_test)
        self.test_accuracy = accuracy_score(self.y_test, test_pred)
        self.test_precision = precision_score(self.y_test, test_pred, average = 'macro')
        self.test_recall = recall_score(self.y_test, test_pred, average = 'macro')
        self.test_f1score = f1_score(self.y_test, test_pred, average = 'macro')
        print("accuracy on test set: ", self.test_accuracy , "\n Precision on test set: " , self.test_precision , "\n Recall on test set: "
             , self.test_recall , "\n f1score : " , self.test_f1score)
        return (self.test_accuracy, self.test_precision, self.test_recall, self.test_f1score)
    
 