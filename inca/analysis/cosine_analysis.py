"""
This file contains the basics to determine the overlap based on softcosine similarity
"""

from ..core.analysis_base_class import Analysis
from ..core.database import client, elastic_index, scroll_query
import os
import logging
import pandas as pd
import gensim
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import SparseMatrixSimilarity
import time
import datetime
import networkx as nx
from itertools import groupby, islice
from tqdm import tqdm


logger = logging.getLogger("INCA")


class cosine_similarity(Analysis):
    """Compares documents from source and target, showing their cosine distance"""

    def window(self, seq, n):
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result

    def fit(
        self,
        source,
        target,
        sourcetext="text",
        sourcedate="publication_date",
        targettext="text",
        targetdate="publication_date",
        keyword_source=None,
        keyword_target=None,
        keyword_source_must=False,
        keyword_target_must=False,
        condition_source=None,
        condition_target=None,
        days_before=None,
        days_after=None,
        merge_weekend=False,
        threshold=None,
        from_time=None,
        to_time=None,
        to_csv=False,
        destination="comparisons",
        to_pajek=False,
        filter_above=0.5,
        filter_below=5,
    ):
        """
        source/target = doctype of source/target (can also be a list of multiple doctypes)
        sourcetext/targettext = field where text of target/source can be found (defaults to 'text')
        sourcdate/targetedate = field where date of source/target can be found (defaults to 'publication_date')
        keyword_source/_target = optional: specify keywords that need to be present in the textfield; list or string (lowercase)
        keyword_source/_target_must = optional: In case of a list, do all keywords need to appear in the text (logical AND) or does at least one of the words need to be in the text (logical OR). Defaults to False (logical OR)
        condition_source/target = optional: supply the field and its value as a dict as a condition for analysis, e.g. {'topic':1} (defaults to None)
        days_before = days target is before source (e.g. 2); days_after = days target is after source (e.g. 2) -> either both or none should be supplied. Additionally, merge_weekend = True will merge articles published on Saturday and Sunday.
        threshold = threshold to determine at which point similarity is sufficient; if supplied only the rows who pass it are included in the dataset
        from_time, to_time = optional: specifying a date range to filter source and target articles. Supply the date in the yyyy-MM-dd format.
        to_csv = if True save the resulting data in a csv file - otherwise a pandas dataframe is returned
        destination = optional: where should the resulting datasets be saved? (defaults to 'comparisons' folder)
        to_pajek = if True save - in addition to csv/pickle - the result (source, target and similarity score) as pajek file to be used in the Infomap method (defaults to False) - not available in combination with days_before/days_after parameters
        filter_above = Words occuring in more than this fraction of all documents will be filtered
        filter_below = Words occuring in less than this absolute number of docments will be filtered
        """
        now = time.localtime()

        logger.info(
            "The results of the similarity analysis could be inflated when not using the recommended text processing steps (stopword removal, punctuation removal, stemming) beforehand"
        )

        # Construct source and target queries for elasticsearch
        if isinstance(source, list):  # multiple doctypes
            source_query = {
                "query": {
                    "bool": {
                        "filter": {"bool": {"must": [{"terms": {"doctype": source}}]}}
                    }
                }
            }
        elif isinstance(source, str):  # one doctype
            source_query = {
                "query": {
                    "bool": {
                        "filter": {"bool": {"must": [{"term": {"doctype": source}}]}}
                    }
                }
            }

        if isinstance(target, list):  # multiple doctypes
            target_query = {
                "query": {
                    "bool": {
                        "filter": {"bool": {"must": [{"terms": {"doctype": target}}]}}
                    }
                }
            }
        elif isinstance(target, str):  # one doctype
            target_query = {
                "query": {
                    "bool": {
                        "filter": {"bool": {"must": [{"term": {"doctype": target}}]}}
                    }
                }
            }

        # Change query if date range was specified
        source_range = {"range": {sourcedate: {}}}
        target_range = {"range": {targetdate: {}}}
        if from_time:
            source_range["range"][sourcedate].update({"gte": from_time})
            target_range["range"][targetdate].update({"gte": from_time})
        if to_time:
            source_range["range"][sourcedate].update({"lte": to_time})
            target_range["range"][targetdate].update({"lte": to_time})
        if from_time or to_time:
            source_query["query"]["bool"]["filter"]["bool"]["must"].append(source_range)
            target_query["query"]["bool"]["filter"]["bool"]["must"].append(target_range)

        # Change query if keywords were specified
        if isinstance(keyword_source, str) == True:
            source_query["query"]["bool"]["filter"]["bool"]["must"].append(
                {"term": {sourcetext: keyword_source}}
            )
        elif isinstance(keyword_source, list) == True:
            if keyword_source_must == True:
                for item in keyword_source:
                    source_query["query"]["bool"]["filter"]["bool"]["must"].append(
                        {"term": {sourcetext: item}}
                    )
            elif keyword_source_must == False:
                source_query["query"]["bool"]["should"] = []
                source_query["query"]["bool"]["minimum_should_match"] = 1
                for item in keyword_source:
                    source_query["query"]["bool"]["should"].append(
                        {"term": {sourcetext: item}}
                    )
        if isinstance(keyword_target, str) == True:
            target_query["query"]["bool"]["filter"]["bool"]["must"].append(
                {"term": {targettext: keyword_target}}
            )
        elif isinstance(keyword_target, list) == True:
            if keyword_target_must == True:
                for item in keyword_target:
                    target_query["query"]["bool"]["filter"]["bool"]["must"].append(
                        {"term": {targettext: item}}
                    )
            elif keyword_target_must == False:
                target_query["query"]["bool"]["should"] = []
                target_query["query"]["bool"]["minimum_should_match"] = 1
                for item in keyword_target:
                    target_query["query"]["bool"]["should"].append(
                        {"term": {targettext: item}}
                    )

        # Change query if condition_target or condition_source is specified
        if isinstance(condition_target, dict) == True:
            target_query["query"]["bool"]["filter"]["bool"]["must"].append(
                {"match": condition_target}
            )
        if isinstance(condition_source, dict) == True:
            source_query["query"]["bool"]["filter"]["bool"]["must"].append(
                {"match": condition_source}
            )

        # Retrieve source and target articles as generators
        source_query = scroll_query(source_query)
        target_query = scroll_query(target_query)

        # Make generators into lists and filter out those who do not have the specified keys (preventing KeyError)
        target_query = [
            a
            for a in target_query
            if targettext in a["_source"].keys() and targetdate in a["_source"].keys()
        ]
        source_query = [
            a
            for a in source_query
            if sourcetext in a["_source"].keys() and sourcedate in a["_source"].keys()
        ]

        # Target and source texts (split)
        target_text = []
        for doc in target_query:
            target_text.append(doc["_source"][targettext].split())
        source_text = []
        for doc in source_query:
            source_text.append(doc["_source"][sourcetext].split())

        logger.info("Preparing dictionary")
        dictionary = Dictionary(source_text + target_text)
        logger.info(
            "Removing all tokens that occur in less than {} documents or in more than {:.1f}% or all documents from dictionary".format(
                filter_below, filter_above * 100
            )
        )
        dictionary.filter_extremes(no_below=filter_below, no_above=filter_above)
        logger.info("Preparing tfidf model")
        tfidf = TfidfModel(dictionary=dictionary)

        # extract additional information from sources
        source_dates = [doc["_source"][sourcedate] for doc in source_query]
        source_ids = [doc["_id"] for doc in source_query]
        source_doctype = [doc["_source"]["doctype"] for doc in source_query]
        source_dict = dict(zip(source_ids, source_dates))
        source_dict2 = dict(zip(source_ids, source_doctype))

        # extract information from targets
        target_ids = [doc["_id"] for doc in target_query]
        target_dates = [doc["_source"][targetdate] for doc in target_query]
        target_dict = dict(zip(target_ids, target_dates))
        target_doctype = [doc["_source"]["doctype"] for doc in target_query]
        target_dict2 = dict(zip(target_ids, target_doctype))

        # If specified, comparisons compare docs within sliding date window
        if days_before != None or days_after != None:
            logger.info("Performing sliding window comparisons...")
            # merge queries including identifier key
            for i in source_query:
                i.update({"identifier": "source"})
            for i in target_query:
                i.update({"identifier": "target"})
            source_query.extend(target_query)

            # sourcedate and targetdate need to be the same key (bc everything is done for sourcedate)
            if targetdate is not sourcedate:
                logger.info(
                    "Make sure that sourcedate and targetdate are the same key."
                )

            else:
                # convert dates into datetime objects
                for a in source_query:
                    if isinstance(a["_source"][sourcedate], datetime.date) == True:
                        pass  # is already datetime object
                    else:
                        a["_source"][sourcedate] = [
                            int(i) for i in a["_source"][sourcedate][:10].split("-")
                        ]
                        a["_source"][sourcedate] = datetime.date(
                            a["_source"][sourcedate][0],
                            a["_source"][sourcedate][1],
                            a["_source"][sourcedate][2],
                        )

                # sort query by date
                source_query.sort(key=lambda item: item["_source"][sourcedate])

                # create list of all possible dates
                d1 = source_query[0]["_source"][sourcedate]
                d2 = source_query[-1]["_source"][sourcedate]
                delta = d2 - d1
                date_list = []
                for i in range(delta.days + 1):
                    date_list.append(d1 + datetime.timedelta(i))

                # create list of docs grouped by date (dates without docs are empty lists)
                grouped_query = []
                for d in date_list:
                    dt = []
                    for a in source_query:
                        if a["_source"][sourcedate] == d:
                            dt.append(a)
                    grouped_query.append(dt)
                # Optional: merges saturday and sunday into one weekend group
                # Checks whether group is Sunday, then merge together with previous (saturday) group.
                if merge_weekend == True:
                    grouped_query_new = []
                    for group in grouped_query:
                        # if group is sunday, extend previous (saturday) list, except when it is the first day in the data.
                        # if empty, append empty list
                        if not group:
                            grouped_query_new.append([])
                        elif group[0]["_source"][sourcedate].weekday() == 6:
                            if not grouped_query_new:
                                grouped_query_new.append(group)
                            else:
                                grouped_query_new[-1].extend(group)
                        # for all other weekdays, append new list
                        else:
                            grouped_query_new.append(group)
                    grouped_query = grouped_query_new

                # Sliding window starts here... How it works:
                # A sliding window cuts the documents into groups that should be compared to each other based on their publication dates. A list of source documents published on the reference date is created. For each of the target dates in the window, the source list is compared to the targets, the information is put in a dataframe, and the dataframe is added to a list. This process is repeated for each window. We end up with a list of dataframes, which are eventually merged together into one dataframe.

                len_window = days_before + days_after + 1
                source_pos = (
                    days_before
                )  # source position is equivalent to days_before (e.g. 2 days before, means 3rd day is source with the index position [2])
                n_window = 0

                for e in tqdm(self.window(grouped_query, n=len_window)):
                    n_window += 1
                    df_window = []

                    source_texts = []
                    source_ids = []
                    if not "source" in [l2["identifier"] for l2 in e[source_pos]]:
                        pass

                    else:
                        for doc in e[source_pos]:
                            try:
                                if doc["identifier"] == "source":
                                    # create sourcetext list to compare against
                                    source_texts.append(
                                        doc["_source"][sourcetext].split()
                                    )
                                    # extract additional information
                                    source_ids.append(doc["_id"])
                            except:
                                logger.error(
                                    "This does not seem to be a valid document"
                                )
                                print(doc)

                        # create index of source texts
                        query = tfidf[[dictionary.doc2bow(d) for d in source_texts]]

                        # iterate through targets
                        for d in e:
                            target_texts = []
                            target_ids = []

                            for doc in d:
                                try:
                                    if doc["identifier"] == "target":
                                        target_texts.append(
                                            doc["_source"][targettext].split()
                                        )
                                        # extract additional information
                                        target_ids.append(doc["_id"])
                                except:
                                    logger.error(
                                        "This does not seem to be a valid document"
                                    )
                                    print(doc)
                            # do comparison
                            index = SparseMatrixSimilarity(
                                tfidf[[dictionary.doc2bow(d) for d in target_texts]],
                                num_features=len(dictionary),
                            )
                            sims = index[query]
                            # make dataframe
                            try:
                                df_temp = (
                                    pd.DataFrame(
                                        sims, columns=target_ids, index=source_ids
                                    )
                                    .stack()
                                    .reset_index()
                                )
                                df_window.append(df_temp)
                            except Exception as e:
                                logger.info(
                                    "Could not create dataframe; probably, there is nothing to compare here."
                                )
                                logger.debug(e)
                        df = pd.concat(df_window, ignore_index=True)
                        df.columns = ["source", "target", "similarity"]
                        df["source_date"] = df["source"].map(source_dict)
                        df["target_date"] = df["target"].map(target_dict)
                        df["source_doctype"] = df["source"].map(source_dict2)
                        df["target_doctype"] = df["target"].map(target_dict2)

                        # Optional: if threshold is specified
                        if threshold:
                            df = df.loc[df["similarity"] >= threshold]

                        # Make exports folder if it does not exist yet
                        if not os.path.exists(destination):
                            os.mkdir(destination)

                        # Optional: save as csv file
                        if to_csv == True:
                            df.to_csv(
                                os.path.join(
                                    destination,
                                    r"INCA_cosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{n_window}.csv".format(
                                        now=now,
                                        target=target,
                                        source=source,
                                        n_window=n_window,
                                    ),
                                )
                            )
                            # Otherwise: save as pickle file
                        else:
                            df.to_pickle(
                                os.path.join(
                                    destination,
                                    r"INCA_cosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{n_window}.pkl".format(
                                        now=now,
                                        target=target,
                                        source=source,
                                        n_window=n_window,
                                    ),
                                )
                            )

                # Optional: save as pajek file not for days_before/days_after
                if to_pajek == True:
                    logger.info(
                        "Does not save as Pajek file with days_before/days_after because of the size of the files."
                    )

        # Same procedure as above, but without specifying a time frame (thus: comparing all sources to all targets)
        else:

            # Create index out of target texts
            logger.info("Preparing the index out of target texts...")
            index = SparseMatrixSimilarity(
                tfidf[[dictionary.doc2bow(d) for d in target_text]],
                num_features=len(dictionary),
            )

            # Retrieve source IDs and make generator to compute similarities between each source and the index
            logger.info("Preparing the query out of source texts...")
            query = tfidf[[dictionary.doc2bow(d) for d in source_text]]
            query_generator = (item for item in query)

            # Retrieve similarities
            logger.info("Starting comparisons...")

            i = 0
            s_ids = 0
            for doc in query_generator:
                i += 1  # count each round of comparisons
                # if doc is empty (which may happen due to pruning)
                # then we skip this comparison
                if len(doc) == 0:
                    s_ids += 1
                    logger.info("Skipped one empty document")
                    continue

                # sims_list = [index[doc] for doc in query_generator]
                sims = index[doc]

                # make dataframe
                # df = pd.DataFrame(sims_list, columns=target_ids, index = source_ids).stack(). reset_index()
                df = pd.DataFrame([sims]).transpose()
                logger.debug("Created dataframe of shape {}".format(df.shape))
                logger.debug("Length of target_id list: {}".format(len(target_ids)))
                df["target"] = target_ids
                df["source"] = source_ids[s_ids]
                df.columns = ["similarity", "target", "source"]
                df["source_date"] = df["source"].map(source_dict)
                df["target_date"] = df["target"].map(target_dict)
                df["source_doctype"] = df["source"].map(source_dict2)
                df["target_doctype"] = df["target"].map(target_dict2)
                df = df.set_index("source")

                # Optional: if threshold is specified
                if threshold:
                    df = df.loc[df["similarity"] >= threshold]

                # Make exports folder if it does not exist yet
                if not "comparisons" in os.listdir("."):
                    os.mkdir("comparisons")

                # Optional: save as csv file
                if to_csv == True:
                    df.to_csv(
                        os.path.join(
                            destination,
                            r"INCA_cosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{i}.csv".format(
                                now=now, target=target, source=source, i=i
                            ),
                        )
                    )
                # Otherwise: save as pickle file
                else:
                    df.to_pickle(
                        os.path.join(
                            destination,
                            r"INCA_cosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{i}.pkl".format(
                                now=now, target=target, source=source, i=i
                            ),
                        )
                    )

                # Optional: additionally save as pajek file
                if to_pajek == True:
                    G = nx.Graph()
                    # change int to str (necessary for pajek format)
                    df["similarity"] = df["similarity"].apply(str)
                    # change column name to 'weights' to faciliate later analysis
                    df.rename({"similarity": "weight"}, axis=1, inplace=True)
                    # notes and weights from dataframe
                    G = nx.from_pandas_edgelist(
                        df, source="source", target="target", edge_attr="weight"
                    )
                    # write to pajek
                    nx.write_pajek(
                        G,
                        os.path.join(
                            destination,
                            r"INCA_cosine_{source}_{target}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{i}.net".format(
                                now=now, target=target, source=source, i=i
                            ),
                        ),
                    )

                s_ids += 1  # move one doc down in source_ids

                logger.info(
                    "Done with source " + str(i) + " out of " + str(len(source_text))
                )

    def predict(self, *args, **kwargs):
        pass

    def quality(self, *args, **kwargs):
        pass

    def interpretation(self, *args, **kwargs):
        pass
