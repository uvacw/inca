import sys
import pandas as pd

# from ..core import search_utils
# from ..core import database
import logging
import numpy as np
import string
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split

from ..core.analysis_base_class import Analysis
from scipy.sparse import csr_matrix
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score
from sklearn import svm
from datetime import datetime


logger = logging.getLogger("INCA")


class classification(Analysis):
    def __init__(self):
        pass

    def fit(
        self,
        documents,
        x_field,
        label_field,
        add_prediction=False,
        testsize=0.2,
        mindf=0.0,
        maxdf=1.0,
        rand_shuffle=True,
        tfidf=True,
        vocabul=None,
    ):
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
        @param one_pass: Keeps all documents in memory instead of retrieving them twice from ElasticSearch
        """

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
        self.documents_fulltext = []

        counter = 0
        invalidchars = set(string.punctuation)

        for doc in documents:
            counter += 1
            if len(core.basic_utils.dotkeys(doc, x_field)) > 0:
                self.valid_docs.append(doc["_id"])
                self.labels.append(core.basic_utils.dotkeys(doc, label_field))
                self.documents_fulltext.append(core.basic_utils.dotkeys(doc, x_field))

                if counter < 5:
                    text = core.basic_utils.dotkeys(doc, x_field).lower()
                    if any(char in invalidchars for char in text):
                        logger.info(
                            "Punctuation has not been removed. Proceeding without pre-processing."
                        )

            else:
                self.invalid_docs.append(doc["_id"])

        assert len(self.valid_docs) == len(self.labels)

        assert len(self.labels) == len(self.documents_fulltext)
        logger.info(
            "Using one-pass processing. Keeping {} documents in memory".format(
                len(self.documents_fulltext)
            )
        )

        # Extracting word counts as featires from example documents
        # If tfidf is set to True, it extracts the term-frequency-inverse-document-frequency features from the example documents.

        if tfidf:
            self.vectorizer = TfidfVectorizer(
                min_df=mindf, max_df=maxdf, vocabulary=vocabul
            )
        else:
            self.vectorizer = CountVectorizer(
                min_df=mindf, max_df=maxdf, vocabulary=vocabul
            )
        self.fitted = self.vectorizer.fit_transform(
            self.documents_fulltext, self.labels
        )
        self.vocab = np.array(self.vectorizer.get_feature_names())
        logger.info(
            "{} x entries and {} y entries".format(
                self.fitted.shape[0], len(self.labels)
            )
        )
        X_train, self.X_test, y_train, self.y_test = train_test_split(
            self.fitted,
            self.labels,
            test_size=testsize,
            shuffle=rand_shuffle,
            random_state=42,
        )
        self.model = SGDClassifier(
            loss="hinge", penalty="l2", alpha=1e-3, max_iter=1000, random_state=42
        ).fit(X_train, y_train)
        if add_prediction == True:
            self.train_predictions = self.model.predict(X_train)
        else:
            self.train_predictions = None

        return (self.vocab, self.fitted, self.labels)

    def predict(self, documents=None, x_field=None, **kwargs):
        """
        This method performs classification of new unseen documents.\n
        @param documents: the documents to classify.
        @type documents: iterable, or a scipy sparse csr matrix of features (representing term frequencies or tfidf values).
        @param x_field: The nested field name that contains the text articles to be classified. Ideally nested within the '_source
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
            logger.info(
                "Since no documents were inputted, this shall run the trained model on the test dataset reserved as 20% of the original labeled example dataset."
            )
        else:
            if type(documents[0]) is str:
                logger.info(
                    "It seems that the input documents are a list of strings, proceeding without extracting any specific field"
                )
                documents = self.vectorizer.transform(documents)
            elif type(documents[0]) is dict and x_field is not None:
                logger.info(
                    "It seems that the input documents are a list of dicts, extracting the provided x_field"
                )
                documents = self.vectorizer.transform(
                    (core.basic_utils.dotkeys(doc, x_field) for doc in documents)
                )
            else:
                raise Exception(
                    "You have to input either nothing, or a list of strings, or a list of dicts together with the x_field"
                )

        self.predictions = self.model.predict(documents)
        print("no_of predictions : ", len(self.predictions))

        return self.predictions

    def quality(self, **kwargs):
        """
        This method has the functionality to report on the quality of the underlying Classification (trained) model which was created as a         random subset as a proportion of the input documents.\n
        The size of the test set is controlled through the parameter 'testsize' of the fit method of the Classification analyser object.           The default proportion is 0.2, with random shuffle set as True.\n
        It calculates the categorization accuracy, precision, recall and f1-score on the test set of examples.\n

        """
        # make the test predictions as an attribute.

        test_pred = self.model.predict(self.X_test)
        self.test_accuracy = accuracy_score(self.y_test, test_pred)
        self.test_precision = precision_score(self.y_test, test_pred, average="macro")
        self.test_recall = recall_score(self.y_test, test_pred, average="macro")
        self.test_f1score = f1_score(self.y_test, test_pred, average="macro")
        print(
            "accuracy on test set: ",
            self.test_accuracy,
            "\n Precision on test set: ",
            self.test_precision,
            "\n Recall on test set: ",
            self.test_recall,
            "\n f1score : ",
            self.test_f1score,
        )
        return {
            "accuracy": self.test_accuracy,
            "precision": self.test_precision,
            "recall": self.test_recall,
            "f1": self.test_f1score,
        }
