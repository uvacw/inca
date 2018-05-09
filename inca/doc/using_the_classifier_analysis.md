# INCA Analysis functionality: Classifying documents

## What it is

Classification of text documents is a supervised learning task.
This analysis functionality built into INCA trains a classifier (algorithm) on a set of labeled document examples provided (called the train set). It then uses the trained model to classify new, previously unseen documents into different classes/categories. For this, the following takes place:

1. Classifier Model Training:

(a) Takes in an input set of labeled documents, in form of an iterable that iterates over an ElasticSearch stored doctype. By labeled we mean that each document text is accompanied by a corresponding label field that denotes its class. As an example, for news articles, possible categoriy labels could be sports, politics, international news, etc. 

(b) Extracts features, in form of term frequencies, or term frequency-inverse document frequencies from the text documents.

(c) Splits the labeled examples (their extracted features) into a train and test set, in a 80:20 ratio. 

(d) The model is fit on the training set.


2. Evaluation on a Test Set: 

The reserved test set from the initial labeled example documents inputted, is used to evaluate the quality of the model in form of standard metrics such as categorization accuracy, precision, recal and F1 score.

3. The trained model is used on unseen (and unlabeled) documents, in order to predict the class of each document.


## Example

For this example, we assume that you have a running instance of Elastic Search.

### Collect some documents

First of all, we need some documents. For instance, we could scrape them.

```python
from inca import Inca()
myinca = Inca()
myinca.rssscrapers.nu()
```

Let's verify we got them, for instance using `myinca.database.list_doctypes()` or `myinca.database.doctype_examples('nu')`.

### Annotate the documents

A typical task could be to predict whether the documents contain a specific frame or topic. We would then hand-code (annotate) some of these articles and use these annotations as training data. Let us for demonstration purposes create a random annotation and assign a 0 or 1 to each document. 

```python
import random
docs = myinca.database.doctype_generator('nu')
# for technical reasons, we need to specify a field as 'input' for the random processor.
# I just choose META as it is always present
p = myinca.processing.randomfield('nu',field='META', new_key='randomnumber', save =True, force = True)
randomnumbers = [d['_source']['randomnumber'] for d in p]
```


### Train and test the classifier

First, we to specifify which documents to use for training and testing the classifier. For instance, we can create a generator that gives us all nu.nl-articles. 
Then, we fit the classifier. Let's see whether we can predict `randomnumber` by `title` (hopefully, we can't ;-) )
You can vary the mindf and maxdf such that: 0.0<=mindf<maxdf<=1.0. Please note that the defaults have been given as mindf=0.0, and maxdf = 1.0. (Refer to documentation.)

```python
g = myinca.database.doctype_generator('nu')
myinca.analysis.classification.fit(g, x_field = '_source.title', label_field = '_source.randomnumber')
```


3. Trying the predict method. Please insert an iterable over documents that you wish to classify. If None (the default) is specified, then the method simply returns the class predictions on the test set which was internally created during the fit method on the same Classification object.

```python
myinca.analysis.classification.predict()
```

# 4. Using the quality method, to return evaluation metrics of how the model fared on the internally created test data set. 

```python
myinca.analysis.classification.quality()
```

As you see, we could as well throw a coin - as we would expect!