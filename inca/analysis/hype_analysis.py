import re

from nltk.corpus import stopwords
stopwords=stopwords.words('dutch')
import nltk.corpus
from nltk.text import TextCollection
from string import punctuation

from gensim import corpora
from gensim import models

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english')
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

import pandas as pd

class Hype():
                    
     def hype_preprocess(self, documents):
          docs = []
          cleandocs = []
          for i in documents:
               docs += doc[i]['_source']['text']
          for w in docs:  #preprocess:
               cleandocs = [word.lower() for word in docs] #make lowercase
               cleandocs = ["".join([word for word in cleandocs if word not in punctuation])for doc in cleandocs] #remove punctuation
               cleandocs = [re.sub('\d', " ", word) for word in cleandocs]  #remove numbers
               cleandocs = [" ".join(word for word in w.split() if word not in stopwords)]#remove stopwords
             #stem words??

          for t in cleandocs:
               alltext += t.split() #make bag of words
               #make bag of words per article?? # necessary?
               
                
     def hype_tfidf(self, word): #prints a list of articles(publication date) and the tfidf score for the specified word or words
          mycollection = nltk.TextCollection([alltext, "list of texts here"])
          
          for e in documents:
               try:
                    s = mycollection.tf_idf('word', e['_source']['text'])
                    print (e['_type'], e['_source']['publication_date'], s)
               except:
                    print (e['_type'], e['_source']['publication_date'], 'no text')

          #with dataframe
          df1 = pd.DataFrame(columns=['Type', 'Publication Date', 'Tf-idf'])
          for e in docs:
               try:
                    s = mycollection.tf_idf('hij', e['_source']['text'])
                    df1 = df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':s}, index=[0]), ignore_index=True)
               except:
                    df1 = df1.append(pd.DataFrame({'Type':e['_type'], 'Publication Date':e['_source']['publication_date'], 'Tf-idf':'no text'}, index=[0], ignore_index=True)

          

#Example of result for def hype_tfidf
#nu 2018-05-09T08:45:17 0.0
#nu 2018-05-09T09:08:47 0.0
#nu 2018-05-09T08:48:29 0.0
#nu 2018-05-09T09:09:05 0.0
#nu 2018-05-09T09:03:23 no text
#nu 2018-05-09T09:01:52 0.0
#nu 2018-05-09T09:05:43 0.0
#nu 2018-05-09T08:50:54 0.0
#nu 2018-05-09T08:45:04 0.0
#nu 2018-05-09T09:06:41 0.0
#gelderlander (www) 2018-05-09T08:41:23 0.0
#gelderlander (www) 2018-05-09T07:02:42 0.0
#gelderlander (www) 2018-05-09T07:18:47 0.0

# now aggregate per day and plot
# use pandas

     def hype_cluster():
          texts= []
          for d in docs:
               try:
                    texts.append(d['_source']['text'])
               except:
                    texts.append('no text')

          #make model
          print("Making model")
          X = vectorizer.fit_transform(texts) #maybe loop here to count articles?

          #clustering
          k = 10 #number of clusters
          km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1)
          km.fit(X)
          print('done')

          #Top clusters  
          print("Top terms per cluster:")
          order_centroids = km.cluster_centers_.argsort()[:, ::-1]
          terms = vectorizer.get_feature_names()
          for i in range(k):
               print("Cluster %d:" % i, end='')
               for ind in order_centroids[i, :10]:
                    print(' %s' % terms[ind], end='')
               print()

          #distance between clusters?
     

          #Plotting model/clusters
          print('Plotting clusters')

          #centers = km.cluster_centers_
          
          plt.plot()
          plt.title('k means centroids')
          plt.scatter(order_centeroids[:,0], order_centeroids[:,1], marker="x", color='r') #centers could also be plotted instead 
          plt.show()

          #Predicting for new texts
          #Tells you in which cluster a new text is placed
          print("Predict for new texts")
          Y = vectorizer.transform(["new texts here"])
          prediction = model.predict(Y)
          print(prediction)
          #example result for 5 new texts and 3 clusters: [1, 2, 2, 1, 3]

          
#http://scikit-learn.org/stable/auto_examples/text/document_clustering.html     #https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
#http://brandonrose.org/clustering
#http://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
#http://scikit-learn.org/stable/auto_examples/cluster/plot_ward_structured_vs_unstructured.html#sphx-glr-auto-examples-cluster-plot-ward-structured-vs-unstructured-py
#http://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
#sklearn.cluster.AgglomerativeClustering
#https://pythonprogramminglanguage.com/kmeans-text-clustering/
#https://stackoverflow.com/questions/27585918/how-does-kmeans-know-how-to-cluster-documents-when-we-only-feed-it-tfidf-vectors?rq=1
#https://stackoverflow.com/questions/28160335/plot-a-document-tfidf-2d-graph/28205420#28205420
