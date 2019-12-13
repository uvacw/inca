"""
This file contains the basics to generate timelines

"""

import pandas
import numpy
from ..core.database import client, elastic_index
import logging
from ..core.analysis_base_class import Analysis

logger = logging.getLogger("INCA")


class timeline_generator(Analysis):
    """Generates timelines from elasticsearch string queries"""

    def fit(
        self,
        queries,
        timefield,
        granularity="week",
        querytype="count",
        field=None,
        from_time=None,
        to_time=None,
        filter=None,
    ):
        """returns a pandas dataframe """
        if type(queries) == str:
            queries = [queries]
        if type(querytype) == str:
            querytype = [querytype] * len(queries)
        if field and type(field) == str or type(field) == type(None):
            field = [field] * len(queries)

        assert len(queries) == len(
            querytype
        ), "there should be one querytype for each query"
        if field:
            assert len(queries) == len(
                field
            ), "if specified, there should be a field for each query"

        target_dataframe = False
        prepend = []

        for num, q, qt, f in zip(range(len(queries)), queries, querytype, field):
            logger.debug(num, q, qt, f)
            if qt != "count" and not field:
                logger.info(
                    "metrics require a field to which the metric should be applied!,"
                    "which field should be {qt}-ed".format(**locals())
                )

            # basic elastic query to select documents for each timeseries
            elastic_query = {
                "query": {"bool": {"must": [{"query_string": {"query": q}}]}},
                "aggs": {
                    "timeline": {
                        "date_histogram": {"field": timefield, "interval": granularity}
                    }
                },
            }
            if qt != "count":
                elastic_query["aggs"]["timeline"].update(
                    {"aggs": {"metric": {qt: {"field": f}}}}
                )

            # add time range if from or to time is specified
            time_range = {timefield: {}}
            if from_time:
                time_range[timefield].update({"gte": from_time})
            if to_time:
                time_range[timefield].update({"lte": to_time})

            # apply filter if specified
            if type(filter) == str:
                elastic_query["query"]["bool"]["must"].append(
                    {"query_string": {"query": filter}}
                )
            elif type(filter) == dict:
                elastic_query["query"]["bool"]["must"].append({"match": filter})

            if from_time or to_time:
                elastic_query["query"]["bool"]["must"].append({"range": time_range})

            logger.debug("elastic query = {elastic_query}".format(**locals()))
            res = client.search(elastic_index, body=elastic_query, size=0)
            logger.debug("found {res[hits][total]} results in total".format(**locals()))

            if qt == "count":
                df = pandas.DataFrame(res["aggregations"]["timeline"]["buckets"])
            else:
                df = pandas.DataFrame(
                    [
                        {
                            "doc_count": b["metric"]["value"],
                            "key_as_string": b["key_as_string"],
                        }
                        for b in res["aggregations"]["timeline"]["buckets"]
                    ]
                )
            logger.debug("dataframe: {df}".format(**locals()))
            num += 1
            longer = len(q) > 10 and "..." or "   "
            new_name = "{num}. {q:.10}{longer}".format(**locals())

            df = df.rename(
                columns={"doc_count": new_name, "key_as_string": "timestamp"}
            )

            if type(target_dataframe) == bool and target_dataframe == False:
                if df.empty:
                    prepend.append(new_name)
                    continue
                else:
                    target_dataframe = df[["timestamp", new_name]]
            elif df.empty:
                target_dataframe[new_name] = numpy.nan
            else:
                target_dataframe = target_dataframe.merge(
                    df[["timestamp", new_name]], on="timestamp", how="outer"
                )

            if prepend:
                colnames = [
                    name for name in target_dataframe.columns if name != "timestamp"
                ]
                for empty_column in prepend:
                    target_dataframe[empty_column] = numpy.nan
                ordered_cols = ["timestamp"] + prepend + list(colnames)
                target_dataframe = target_dataframe[ordered_cols]
                prepend = []

        if not (type(target_dataframe) == bool and target_dataframe == False):
            target_dataframe = target_dataframe.replace(numpy.nan, 0)
            return target_dataframe
        else:
            logger.info("Empty result")
            return pandas.DataFrame()
