import logging
import numpy as np
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1score, precision_recall_fscore_support
from sklearn.cross_validation import KFold



logger = logging.getLogger(__name__)

class classification(Analysis):
    


    def fit(self, documents, _id , x_field, label_field, add_prediction=False, **kwargs, n_kfold_splits = 1):
        """
        This method should train a model on the input documents.\n
        @param documents: the documents (dictionaries) to train on
        """
         
        """
        @type documents: iterable
        @param _id: 
        @type _id:
        @param x_field: The name of the field containing the training text data 
        @type x_field: str
        @label_field: Name of the field that contains the labels
        """
        #To keep add_prediction or not?This is similar to the y_label above. Am i supposed to make something exclusive to my own, or not? 
        """
        @param add_prediction: this switch signals the mutation of the train set documents by adding a key, value pair document.\
                               If given (add_prediction == True), then key=add_prediction and value should be the model's output:\n
                                 * For classification tasks: class labels\n
                                 * For clustering tasks: assigned cluster\n
        @type add_prediction: str
        
        """
        #Segregating documents based on whether they have text or not, into 'valid_docs and invalid_docs
        invalid_docs = []
        valid_docs = []
        for doc in documents:
            if doc['_source'][x_field] not in doc:
                #Be careful, in elasticsearch or json objects, this may be a nested dictionary.
                invalid_docs.append(doc['_id'])
                logger.warning("Document has text field missing.")
            else: 
                valid_docs.append(doc['_id'])
            
            else:
                text = doc['_source'][x_field].lower()
                for word in text:
                    if word not in string.punctuation or in stopwords:
                        raise ValueError('Either punctuation or stopwords have not been removed. Please preprocess and retry.')
        
        y = (doc["_source"]["category"] for doc in newdocs2 if doc["_id"] in valid_docs2)
        labels_list = []
        
        for i in y:
            labels_list.append(i)
        labels = pd.DataFrame({'col':label})

        
        print(type(labels), labels.shape)

        vectorizer = CountVectorizer()
        tfidf_transformer = TfidfTransformer()
       
        counts = vectorizer.fit(doc[x_field] for doc in documents if doc['_id'] in valid_docs)
        #vocab = np.array(vectorizer.get_feature_names())
        '''
        #Sample wthout replacement, 80% of this data as train, and remaining 20% as test.
        N = int(0.8*wordvec.shape[0])
        
        i = np.random.choice(np.arange(wordvec.shape[0]), N, replace=False)         
        train_data_tf = wordvec[i]   
        #Yet to create the master test set. To be constructed using the remaining indices not used to build traindata

        labels_train_full = labels[:N]
        labels_test_full = label[N:]
        '''
        tfidf_full_data = tfidf_transformer.fit_transform(counts)
        
        X_train, self.X_test, y_train, self.y_test = train_test_split(tfidf_full_data, labels, test_size=0.20, shuffle = True, random_state=42)
        self.clf =  SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, max_iter=1000, random_state=42).fit(X_train, y_train)
        
        #If predictions for training documents is wanted
        if add_prediction ==True:
            train_predictions = self.clf.predict(X_train)
        else:
            train_predictions = None
        
        #Think about return statement
        return (self.clf, train_predictions)


                                                   
                                                   
    def predict(self, x_field, documents, add_prediction='', **kwargs):
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
        vectorizer = CountVectorizer()
        tfidf_transformer = TfidfTransformer()
        counts_new = vectorizer.fit(doc[x_field] for doc in documents )# if doc['_id'] in valid_docs)
        tfidf_new = tfidf_transformer.fit_transform(counts)

        clf = self.clf.predict(tfidf_new)
        self.predictions = clf.predict(doc['_source'][x_field] for doc in documents)  
        
        #Try and put the predictions into elasticsearch?
        
        #return statement, plus logger.info
                                                          
        return self.predictions

                                                   
                                                   
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

        test_pred = self.clf.predict(self.y_test)
        self.test_accuracy = metrics.accuracy_score(self.y_test, test_pred)
        self.test_precision = metrics.precision_score(self.y_test, test_pred)
        self.test_recall = metrics.recall_score(self.y_test, test_pred)
        self.test_f1score = metrics.f1_score(self.y_test, test_pred)
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

