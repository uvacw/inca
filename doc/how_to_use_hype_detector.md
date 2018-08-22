# How to use the Hype Detector

## What is it?

The hype detector aims to be a tool to identify sudden changes in words/phrases and to identify events in sets of documents. There are two ways to do this, each with separate methods: clustering method or Td-idf method. INCA has two tf-idf functionalities. The first calculates the tf-idf scores for specified search terms, and the second calculates the most important words based on their tf-idf scores per day.

### 1) Hype_cluster class

The fit method in the Hype_cluster class creates clusters from the texts. It receives texts from the Inca database, where the news article is stored in a dict. The method first takes the text from the location specified as textkey (for example the keys 'text' or 'title' could be used (['_source']['text'])). Then, it creates a model and clusters the texts using the Kmeans clustering algorithm (from SciKit Learn). The desired number of clusters must be specified before running the algorithm. Finally, it prints the top ten words in each cluster.

The plot method in the Hype_cluster class plots the ordered centroids from the clusters created with the fit method. The centroids are marked with an X.

The predict method in the Hype_cluster class predicts in which cluster (from the clusters created with the fit method) a new text would be placed. It requires a new set of documents stored in the Inca database (as in the fit method). It uses the same key specified in the creation of the model and clusters created in the fit method. Finally, it prints the number of cluster for each new text.

Example:
```python
from inca import Inca
myinca = Inca()
docsgen = myinca.database.doctype_generator('nu') # train on one dataset
myinca.analysis.hype_cluster.fit(docsgen, textkey='text', N_clusters=5)
docsgen = myinca.database.doctype_generator('nu') # predict on either same or other dataset
results = myinca.analysis.hype_cluster.predict(docsgen)

print(next(results))
```


### 2) Hype_tfidf class

The fit method in the Hype_tfidf class calculates a Tf-Idf score for each document that is provided. It receives texts from the Inca database, where the news article is stored in a dict. The method first takes the text from the location specified as textkey (for example the keys 'text' or 'title' could be used (['_source']['text'])). Then, it calculates the tf-idf score for the specified word or phrase (searchterms). The scores are saved in a pandas dataframe where the article can be identified by publication date and source (eg newspaper title) of the article.
Note: does not work with documents obtained through a generator (generators have no len)

The plot method in the Hype_tfidf class plots the dataframe created in the fit method. It plots the tfidf score per article. 


Example:

```python
from inca import Inca
myinca = Inca()
docs = list(myinca.database.doctype_generator('nu'))
results = myinca.analysis.hype_tfidf.fit(docs, searchterm = 'trump', textkey='text')

```

Aggregate the results per day:
```
import pandas as pd
results.index = pd.DatetimeIndex(results['Publication Date'].map(pd.to_datetime))
perday = results['Tf-idf'].groupby(results.index.date).sum()
```

And then we can use pandas methods to analyze the dataframe:
```
perday.describe()
perday.plot()
```

### 3) Hype_tfidf_perday class
The fit method concatenates documents per day and finds the most important words per day based on their tf-idf scores. Like the hype_tfidf class, it receives texts from the Inca database, where news articles are stored in a dict. The method takes the text from the location that is specified as textkey (e.g. 'title', 'text', 'text_remove_stopwords'). It concatenates the articles per day and calculates the tf-idf scores. Then, the most important words and their corresponding tf-idf scores are saved in a pandas dataframe together with the publication date.

Example:
```python
from inca import Inca
myinca = Inca()
docs = list(myinca.database.doctype_generator('nu'))
results = myinca.analysis.hype_tfidf_perday.fit(docs, textkey='text')

```

By default, the number of most important words to retrieve per day is set to 5. You can change this number by specifying the top_n parameter:
```python
results = myinca.analysis.hype_tfidf_perday.fit(docs, textkey='text', top_n=10)

```

Note that the tf-idf scores are based on texts including stopwords. To exclude stopwords, first use the stopword removal functionality, and then specify the textkey as 'text_remove_stopwords'.

```python
from inca import Inca
myinca = Inca()
p = [e for e in myinca.preprocessing.remove_stopwords('nu', 'text', stopwords='dutch', save=True)]
docs = list(myinca.database.doctype_generator('nu'))
results = myinca.analysis.hype_tfidf_perday.fit(docs, textkey='text_remove_stopwords')

```
