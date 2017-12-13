import sys
sys.executable
sys.path.append('C:/Users/Payal/Documents/GitHub/pattern/')
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
from sklearn.metrics import f1_score, precision_recall_fscore_support, accuracy_score
from sklearn.cross_validation import KFold
from core.analysis_base_class import Analysis
from scipy.sparse import csr_matrix
from sklearn.linear_model import SGDClassifier



logger = logging.getLogger(__name__)


class classification(Analysis):
    
    def __init__(self):
        self.clf = None
        self.vocab = None
        self.train_predictions = None
        self.X_test = None
        self.y_test = None
        self.predictions = None
        self.accuracy = None
        

        
    def fit(self, documents, doctype , x_field, label_field, add_prediction=False, testsize = 0.2, min_df = 0.0, max_df = 1.0, vocabulary = None,  tfidf = True, **kwargs):
        """
        This method should train a model on the input documents.\n
        @param documents: the documents (dictionaries) to train on
        """
         
        """
        @type documents: iterable
        @param _id: 
        @type _id:
        
        DOTKEYS METHOD DOES NOT WORK YET> DO NOT ADD NESTED KEY FUNCTIONALITY YET.
        
        @param x_field: The nested field name that contains the text articles to be classified. Ideally nested within the '_source'
                        field. For instance, to use nested field x2 as text document which is nested as doc['_source']['x1']['x2'], use
                        '_source.x1.x2'
                        (Makes a function call to core.basic_search.utilsdotkeys(dict, key_string) : allows the use of .-separated
                        nested fields such as 'name.firstname' as dict[name][firstname])
        @type x_field: str
        @param label_field: The nested field name that contains the labels.Ideally would be nested within the '_source' field. For
                            instance, to use nested field x2 as label which is nested as doc['_source']['x1']['x2'], use '_source.x1.x2'
                          
        @type label_field: str
        @param add_prediction: this switch signals the mutation of the train set documents by adding a key, value pair document.\
                               If given (add_prediction == True), then key=add_prediction and value should be the model's output:\n
                                 * For classification tasks: class labels\n
                                
        @type add_prediction: str
        
        """
        print(core.search_utils.doctype_fields(doctype))
        #Segregating documents based on whether they have text or not, into 'valid_docs and invalid_docs
        invalid_docs = []
        valid_docs = []
        s=0
        
        for doc in documents:

            if x_field in doc['_source']:
                valid_docs.append(doc['_id'])
                text = doc['_source'][x_field].lower()
                for word in text:
                    if string.punctuation in word: #or in stopwords:
                        logger.info('Either punctuation or stopwords has not been removed. Proceeding without pre-processing.')
                
            else: 
                invalid_docs.append(doc['_id'])

        
        
   
        y = (doc["_source"]["category"] for doc in documents if doc["_id"] in valid_docs)
        labels_list = []

        for i in y:
            labels_list.append(i)
        labels = pd.DataFrame({'col':labels_list})


        
        vectorizer = CountVectorizer( min_df, max_df, vocabulary) 
        counts = vectorizer.fit_transform(doc['_source'][x_field] for doc in documents if doc['_id'] in valid_docs)
        
    #    counts = vectorizer.fit_transform(doc['_source']['textLC'] for doc in documents if doc['_id'] in valid_docs)
        #Extract vocabulary list 
        self.vocab = np.array(vectorizer.get_feature_names())
        
        if tfidf:
            tfidf_transformer = TfidfTransformer()        
            tfidf_full_data = tfidf_transformer.fit_transform(counts)
            
            X_train, self.X_test, y_train, self.y_test = train_test_split(tfidf_full_data, labels, test_size=testsize, shuffle = True, random_state=42)
        
        else:
            X_train, self.X_test, y_train, self.y_test = train_test_split(counts, labels, test_size = testsize, shuffle = True, random_state=42)
        
        self.clf =  SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, max_iter=1000, random_state=42).fit(X_train, y_train)
            
            
        #If predictions for training documents are wanted
        if add_prediction ==True:
            self.train_predictions = self.clf.predict(X_train)
        else:
            self.train_predictions = None
        
        return (self.vocab, self.clf, labels, invalid_docs, valid_docs)
        


                                       
    def predict(self, x_field=None, documents = None, doctype = None, docs=None, **kwargs):
        """
        This method should perform inference on new unseen documents.\n
        @param documents: the documents (dictionaries) to perform inference on
        @type documents: iterable
        @param x_field: The name of the field containing the training text data 
        @type x_field: str
        @param add_prediction: this switch signals the mutation of the given documents by adding a key, value pair document.\
                               If given (add_prediction != ''), then key=add_prediction and value should be the model's output:\n
                                 * For classification tasks: class labels\n
                                 * For clustering tasks: assigned cluster\n
        @type add_prediction: str
        
        
        """
      
        print(type(self.X_test))
        #clf = self.clf.predict(tfidf_new)
        #self.predictions = self.clf.predict(doc['_source'][x_field] for doc in documents)  
        self.predictions = self.clf.predict(self.X_test)
        print('no_of predictions : ',type(self.predictions))
        print('no_ of test examples: ', type(self.y_test))
        self.accuracy = accuracy_score(self.y_test, self.predictions)
        #Try and put the predictions into elasticsearch?
        
                                                          
        return (self.predictions, self.accuracy)


                                                   
                                                   
    def update(self, documents, **kwargs):
        """
        This method should provide online training functionality. In most cases this should basically result in some weight updating based on new evidence.\n
        @param documents: the documents (dictionaries) presented as new evidence to the model. Expected functionality for weight updating
        @type documents: iterable
        """
        
        raise NotImplementedError

       
            
            
            
    def interpretation(self, **kwargs):
        """
        This method should have the functionality to interpret the status of the model after being trained and also document the various design choices\
        (i.e. parameters settings, assumptions, model selection, test method, dataset used). For example it can return a report-like looking formatted string.\n
        Please consider the following as possible model state interpretation:\n
           * For classification tasks depending on the underlying model: coeficient/feature weights, feature selection (random forest)\n
           * For clustering tasks: clusterings members/structure, distributions
        """
        raise NotImplementedError

            
            
            
    def quality(self, **kwargs):
        """
        This method should have the functionality to report on the quality of the underlying (trained) model used for the analysis (on a dataset).\n
           * For classification tasks: retrieval metrics precision, recall, f1-score on a test set internally handled; intrinsic evaluation on hidden evidence.\n
           * For clustering tasks take into consideration application and underlying clustering method since it optimizes against given metric. Example metrics:\n
             - inertia: sum of squared distance for each point to it's closest centroid, i.e., its assigned cluster.\n
             - silhouette
        """
#make the test predictions as an attribute.

        test_pred = self.clf.predict(self.y_test)
        self.test_accuracy = accuracy_score(self.y_test, test_pred)
        self.test_precision = precision_score(self.y_test, test_pred, average = 'macro')
        self.test_recall = recall_score(self.y_test, test_pred, average = 'macro')
        self.test_f1score = f1_score(self.y_test, test_pred, average = 'macro')
        print("accuracy on test set: "+self.test_accuracy + "\n Precision on test set: " + self.test_precision + "\n Recall on test set: "
             + self.test_recall + "\n f1score : " +self.f1score)
        return (self.test_accuracy, self.test_precision, self.test_recall, self.test_f1score)
    
        '''
        #K-fold CV: To be removed
        k_fold = KFold(n=train_data_tf.shape[0], n_splits = n_kfold_splits)
        fscores = []
        precisions = []
        #confusion = np.zeros((n_unique_labels, n_unique_labels )
        count = 0
        for train_indices, test_indices in k_fold:
            print(train_text.shape)
            train_text = train_data_tf[train_indices,:]
            train_y = labels.iloc[train_indices,:]
            
            test_text = train_data_tf[test_indices,:]
            test_y = labels.iloc[test_indices]
            
            tfidf_train = tfidf_transf.fit_transform(train_text)
            self.clf_new = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, max_iter=1000, random_state=42).fit(tfidf_train, train_y)
            predictions = clf_new.predict(test_text)
            
            #confusion += confusion_matrix(test_y, predictions)
            score = f1_score(test_y, predictions, average=None)
            (precision, recall, fscore, support = (precision_recall_fscore_support(test_y, predictions)

            fscores.append(score)
            precisions.append(precision)
            count +=1
            #remove print statement.                                       
            print('metrics for fold  ' + str(count)+ '\n') 
            print(precision_recall_fscore_support(test_y, predictions))
        return (precisions, fscores)
        '''                 
           
            
        raise NotImplementedError

    def plot(self, figure_names, **kwargs):
        """
        This method should write one or more figure files on disk, visualing the model and its behaviour.\n
           * For classification tasks:\n
             - ROC curve: plot the true positive rate against the false positive rate at various threshold settings.\n
             - pre-rec curve: shows the tradeoff between precision and recall at various threshold settings.\n
           * For clustering/unsupervised tasks:\n
             - a 2D visualization of the data reduced to 2D\n
        @param figure_names: the file paths to save the created figures to
        @type figure_names: iterable
        """
        raise NotImplementedError

