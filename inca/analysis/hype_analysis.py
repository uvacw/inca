from ..core.analysis_base_class import Analysis

# import nltk.corpus
# from nltk.text import Text, TextCollection
# from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()

from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import pandas as pd

class hype_cluster(Analysis):

     def fit(self, documents, textkey,  N_clusters):
          '''
          Gets texts from specified documents
          Creates clusters based on the documents provided
          
          Kmeans algorith is used to create the clusters

          Parameters
          ----
          documents:
          News articles stored as dicts in the Inca database

          textkey: string
          The key where the texts can be found (eg 'title' or 'text')

          N_clusters: int
          Desired number of clusters

          Yields
          ----
          Makes model and returns the specified number of clusters. 
          Shows top ten words per cluster
          '''

          self.textkey = textkey
          
          texts= []
          for d in documents:
               try:
                    texts.append(d['_source'][self.textkey])
               except:
                    pass 

          #make model
          print("Making model")
          self.X1 = vectorizer.fit(texts)
          X2 = self.X1.transform(texts)

          #clustering
          self.km = KMeans(n_clusters=N_clusters, init='k-means++', max_iter=100, n_init=1)
          self.km.fit(X2)
          print('done')

          #Top clusters  
          print("Top terms per cluster:")
          self.order_centroids = self.km.cluster_centers_.argsort()[:, ::-1]
          terms = vectorizer.get_feature_names()
          for i in range(N_clusters):
               print("Cluster %d:" % i, end='')
               for ind in self.order_centroids[i, :10]:
                    print(' %s' % terms[ind], end='')
               print()

     def plot(self):
          '''
          Plots the centers of the clusters from model previously fitted

          Yields
          ----
          Plot with the centers of the clusters marked by X
          '''
          print('Plotting cluster centroids')

          #centers = self.km.cluster_centers_
          
          plt.plot()
          plt.title('k means centroids')
          plt.scatter(self.order_centroids[:,0], self.order_centroids[:,1], marker="x") #centers could also be plotted instead
          plt.show()

          
     def predict(self, documents):
          '''
          Predicts in which cluster a new text is placed
          
          Parameters
          ----
          documents:
          News articles stored as dicts in the Inca database
          Will use the same key specifiied above to retrieve texts
          
          Yields
          ----
          A tuple (document, cluster id) 
          '''

          for doc in documents:
               try:
                    Y = self.X1.transform([doc['_source'][self.textkey]])
                    predictions = self.km.predict(Y)
                    yield doc, predictions[0]
               except:
                    pass 
                    
          
          
class hype_tfidf(Analysis):

     def fit(self, documents, searchterm, textkey):
          '''
          Calculates Tf-idf score for each document and creates a dataframe

          Note: does not work with documents obtained through a generator (generators have no len)

          Parameters
          ----
          documents:
          News articles stored as dicts in the Inca database
          
          searchterm: string
          Word or words (phrase) used to calculate the tf-idf score (eg. 'fake news'). Will automatically be lowercased.

          textkey: string
          The key where the texts can be found (eg 'title' or 'text')

          Yields
          ----
          Creates dataframe with news articles from Inca databse. 
          The dataframe includes the source and publication date of the article and the tfidf score for the specified searchterm
          '''

          self.searchterm = searchterm.lower()
          self.textkey = textkey
          textsonly = (e['_source'].get(self.textkey,"") for e in documents)
          vectorizer.fit(textsonly)
               
          self.df1 = pd.DataFrame(columns=['Type', 'Publication Date', 'Tf-idf'])
          for e in documents:
               X = vectorizer.transform([e['_source'].get(self.textkey,'')])
               tfidfscore = X[0, vectorizer.vocabulary_[self.searchterm]]
               #print(self.searchterm, tfidfscore)
               self.df1 = self.df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':tfidfscore}, index=[0]), ignore_index=True)
          return self.df1 

     def plot(self):
          '''
          Plots the dataframe previously created

          Yields
          ----
          A plot showing the tf-idf scores of each article for the specified searchterm
          '''
          plt.title('Tf-idf scores of %s' % self.searchterm)
          plt.scatter(self.df1['Publication Date'], self.df1['Tf-idf'])
          plt.show()
          
     
class hype_tfidf_perday(Analysis):

     def fit(self, documents, textkey):
          '''
          Concatenates documents per day and then calculates Tf-idf score for each day document and creates a dataframe

          Note: does not work with documents obtained through a generator (generators have no len)

          Parameters
          ----
          documents:
          News articles stored as dicts in the Inca database
          
          textkey: string
          The key where the texts can be found (eg 'title' or 'text')

          Yields
          ----
          Creates dataframe with tf-idf scores of most important words per day
          '''

          self.textkey = textkey

          for e in docments:
               # merge documents per day, creating a datarame with date in column 1 and all texts of that day in one single loooooong string in column 2
               # could also be a dict instead with dates as key
               print('TO BE DONE ;-)')

          # then calculate tf idf scores (similar to approah in hype_tfidf class above) based on the day-documents

          # finally, return the three most important words per day
               
               
          return 


          
     
