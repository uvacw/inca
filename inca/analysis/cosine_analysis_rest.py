for doc in source_query:
            try:
                source_tuple.append((doc['_source'][sourcetext], doc['_source'][sourcedate]))
                allsource +=1
            except KeyError:
                pass

        for doc in target_query:
            try:
                target_tuple.append((doc['_source'][targettext], doc['_source'][targetdate]))
                alltarget +=1
            except KeyError:
                pass

        logger.debug("Processed {} sources in total".format(allsource))
        logger.debug("Processed {} targets in total".format(alltarget))
        
        #Make a dict that stores as key how many days apart two documents are and their texts as tuple
    
        for item in source_tuple:
            for item1 in target_tuple:
                day_diff = self.date_comparison(item[1], item1[1])
                if day_diff == "No date" or days_after <= day_diff[2] <= days_before:
                    pass
                else:
                    comparisons[day_diff[2]].append((item[0], item1[0], day_diff[0], day_diff[1]))
                    
        #For every key (documents are within 2 days) every pair of documents is evaluated with regard to their similarity
        
        for key in list(comparisons.keys()):
            if days_before <= key <= days_after:
                all_similarities = []
                documents = [list(item) for item in comparisons[key]]
                for item1 in documents:
                    key1 = item1[0]+"_"+item1[1]
                    overlap[key1].append(item1[2])
                    overlap[key1].append(key)
                    overlap[key1].append(item1[0])
                    overlap[key1].append(item1[1])
                    int_allarticles[key]+=1
                    vect = TfidfVectorizer()
                    tfidf = vect.fit_transform(item1[:2])
                    pairwise_similarity = tfidf * tfidf.T
                    cx = sp.sparse.coo_matrix(pairwise_similarity)
                    ls = self.levenshtein(item1[0], item1[1])
                    for i,j,v in zip(cx.row, cx.col, cx.data):
                        if len(cx.data) == 2:
                            if method == "levenshtein":
                                overlap[key1].append(ls)
                            elif method == "cosine": 
                                overlap[key1].append("no")
                                overlap[key1].append(0)
                            elif method == "both":
                                overlap[key1].append("no")
                                overlap[key1].append(0)
                                overlap[key1].append(ls)
                        else:
                            if v > threshold and i == 0 and j == 1:
                                if method == "levenshtein":
                                    overlap[key1].append(ls)
                                elif method == "cosine": 
                                    overlap[key1].append("yes")
                                    overlap[key1].append(v)
                                elif method == "both":
                                    overlap[key1].append("yes")
                                    overlap[key1].append(v)
                                    overlap[key1].append(ls)
                            elif v <= threshold and i == 0 and j ==1:
                                if method == "levenshtein":
                                    overlap[key1].append(ls)
                                elif method == "cosine": 
                                    overlap[key1].append("no")
                                    overlap[key1].append(v)
                                elif method == "both":
                                    overlap[key1].append("no")
                                    overlap[key1].append(v)
                                    overlap[key1].append(ls)

        for key, value in int_allarticles.items():
            logger.debug("With {} days between the documents: Compared {} documents pairs".format(key, value))

        #Make dataframe where all the information is stored
        d = []
        if method == "levenshtein": 
            for key, value in overlap.items():
                row_dict = {'source_date':value[0], 'day_diff':value[1], 'source':value[2], 'target':value[3], 'levenshtein':value[4]}
                d.append(row_dict)
            data = pd.DataFrame(d, columns = ["source_date", "day_diff", "source", "target", "levenshtein"])
            
        elif method == "cosine":
            for key, value in overlap.items():
                row_dict = {'source_date':value[0], 'day_diff':value[1], 'source':value[2], 'target':value[3], 'made_threshold':value[4], 'cosine':value[5]}
                d.append(row_dict)
            data = pd.DataFrame(d, columns = ["source_date", "day_diff", "source", "target", "made_threshold", "cosine"])
            
        elif method == "both":
            for key, value in overlap.items():
                row_dict = {'source_date':value[0], 'day_diff':value[1], 'source':value[2], 'target':value[3], 'made_threshold':value[4], 'cosine':value[5], 'levenshtein': value[6]}
                d.append(row_dict)
            data = pd.DataFrame(d, columns = ["source_date", "day_diff", "source", "target", "made_threshold", "cosine", "levenshtein"])
            
        if to_csv == True:
            if not 'comparisons' in os.listdir('.'):
                os.mkdir('comparisons')
            data.to_csv(os.path.join('comparisons',"{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))),index = False, header = True)
            return "Saved file {}.csv to comparisons folder".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

        else:
            return data
                
            

               
    def predict(self, *args, **kwargs):
        pass

    def quality(self, *args, **kwargs):
        pass

    def interpretation(self, *args, **kwargs):
        pass
