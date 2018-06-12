import re

from ..core.analysis_base_class import Analysis

import nltk.corpus
from nltk.text import TextCollection

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english') #no dutch

from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import pandas as pd

class hype_cluster(Analysis):

     def fit(self, documents):
          texts= []
          for d in documents:
               try:
                    texts.append(d['_source']['text'])
               except:
                    texts.append('no text')

          #make model
          print("Making model")
          X = vectorizer.fit_transform(texts)

          #clustering
          k = 10 #set number of clusters
          self.km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1)
          self.km.fit(X)
          print('done')

          #Top clusters  
          print("Top terms per cluster:")
          self.order_centroids = self.km.cluster_centers_.argsort()[:, ::-1]
          terms = vectorizer.get_feature_names()
          for i in range(k):
               print("Cluster %d:" % i, end='')
               for ind in self.order_centroids[i, :10]:
                    print(' %s' % terms[ind], end='')
               print()

          #def distance between clusters?

     def plot(self): #needs fixing
          print('Plotting clusters')

          #centers = km.cluster_centers_
          
          plt.plot()
          plt.title('k means centroids')
          plt.scatter(order_centeroids[:,0], order_centeroids[:,1], marker="x", color='r') #centers could also be plotted instead 
          plt.show()

     def predict(self, documents): #needs fixing
          #Tells in which cluster a new text is placed
          print("Predict for new texts")
          for doc in documents:
               Y = (vectorizer.transform([doc]))
               prediction = self.km.predict(Y)
               print(prediction)
          #example result for 5 new texts and 3 clusters: [1, 2, 2, 1, 3]

          
class hype_tfidf(Analysis):

     def fit(self, documents): #needs fixing
          #prints a list of articles(publication date) and the tfidf score for the specified word or words
          mycollection = nltk.TextCollection([documents])

          df1 = pd.DataFrame(columns=['Type', 'Publication Date', 'Tf-idf'])
          for e in documents:
               try:
                    s = mycollection.tf_idf('hij', e['_source']['text'])
                    df1 = df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':s}, index=[0]), ignore_index=True)
               except:
                    df1 = df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':'no text'}, index=[0]), ignore_index=True)
