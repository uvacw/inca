
Classification of text documents/articles is a supervised learning task. This analysis functionality built into INCA trains a classifier (algorithm) on a set of labeled document examples provided (called the train set). It then uses the trained model to classify new, previously unseen documents into different classes/categories. For this, the following takes place:
1. Classifier Model Training:
(a) Takes in an input set of labeled documents, in form of an iterable that iterates over an ElasticSearch stored doctype. By labeled we mean that each document text is accompanied by a corresponding label field that denotes its class. As an example, for news articles, possible categoriy labels could be sports, politics, international news, etc. 
(b) Extracts features, in form of term frequencies, or term frequency-inverse document frequencies from the text documents.
(c) Splits the labeled examples (their extracted features) into a train and test set, in a 80:20 ratio. 
(d) The model is fit on the training set.

2. Evaluation on a Test Set: 
The reserved test set from the initial labeled example documents inputted, is used to evaluate the quality of the model in form of standard metrics such as categorization accuracy, precision, recal and F1 score.

3. The trained model is used on unseen (and unlabeled) documents, in order to predict the class of each document.


Minimal Example:


# 1. Run a scraper: 
client = Inca() # assumes elasticsearch is running
generator_dm = client.database.doctype_generator('dailymail') 
myscraper_dm = inca.scrapers.dailymail_scraper.dailymail()   # make an instance of a nu.nl scraper
myscraper_dm.run() # run the scraper. It takes the last articles from nu.nl and puts them into ELastic Search


# 2. Try the fit method. You can vary the mindf and maxdf such that: 0.0<=mindf<maxdf<=1.0. Please note that the defaults have been given as mindf=0.0, and maxdf = 1.0. (Refer to documentation.)
generator_dm = client.database.doctype_generator('dailymail') 
classifier1 = classification()
vocab, counts, labels= classifier1.fit( documents = generator_dm, x_field = '_source.text', label_field = '_source.category', doctype = 'dailymail' , add_prediction=False, rand_shuffle = True, mindf = 0.2, maxdf = 0.9)

3. Trying the predict method. Please insert an iterable over documents that you wish to classify. If None (the default) is specified, then the method simply returns the class predictions on the test set which was internally created during the fit method on the same Classification object.
predi, acc =classifier1.predict(documents = None)

# 4. Using the quality method, to return evaluation metrics of how the model fared on the internally created test data set. 
generator_dm = client.database.doctype_generator('dailymail')
testacc, testprec, testrecall, testf1 =classifier1.quality()