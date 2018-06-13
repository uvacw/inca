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
          self.X1 = vectorizer.fit(texts)
          X2 = self.X1.transform(texts)

          #clustering
          k = 10 #set number of clusters
          self.km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1)
          self.km.fit(X2)
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

     def plot(self): 
          print('Plotting cluster centroids')

          #centers = self.km.cluster_centers_
          
          plt.plot()
          plt.title('k means centroids')
          plt.scatter(self.order_centroids[:,0], self.order_centroids[:,1], marker="x") #centers could also be plotted instead
          plt.show()

     def predict(self, documents):
          #Tells in which cluster a new text is placed

          print("Predict for new texts")
          prediction = []
          texts2= []
          for doc in documents:
               try:
                    texts2.append(d['_source']['text'])
               except:
                    texts2.append('no text')
                    
          Y = self.X1.transform(texts2)
          
          prediction = self.km.predict(Y)
          print(prediction)
          #example result for 5 new texts and 3 clusters: [1, 2, 2, 1, 3]

          
class hype_tfidf(Analysis):

     def fit(self, documents, searchterms):
          #creates dataframe with articles(by publication date) and the tfidf score for the specified word or words (searchterms)

          self.searchterms = searchterms
          mycollection = nltk.TextCollection([documents])

#          for e in documents:
#               try:
#                    s = mycollection.tf_idf('word', e['_source']['text'])
#                    print (e['_type'], e['_source']['publication_date'], s)
#               except:
#                    print (e['_type'], e['_source']['publication_date'], 'no text')

          self.df1 = pd.DataFrame(columns=['Type', 'Publication Date', 'Tf-idf'])
          for e in documents:
               try:
                    s = mycollection.tf_idf(self.searchterms, e['_source']['text'])
                    self.df1 = self.df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':s}, index=[0]), ignore_index=True)
               except:
                    self.df1 = self.df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':'no text'}, index=[0]), ignore_index=True)
          return self.df1 

     def plot(self):
          plt.title('Tf-idf scores of %s' % self.searchterms)
          plt.scatter(self.df1['Publication Date'], self.df1['Tf-idf'])
          plt.show()
          
     
