"""INCA CSV timeline import functionality

This file contains functionality to create aggregated timelines
and exports them to csv (e.g., frequency counts etc.)

"""

from ..core.document_class import Document
from ..core.basic_utils import dotkeys
from ..analysis.timeline_analysis import timeline_generator
import csv
import chardet
import logging

logger = logging.getLogger("INCA")


class export_timeline(Document):
    def __init__(self, raise_on_fail=False, verbose=True):

        self.processed = 0
        self.failed = 0
        self.failed_ids = []
        self.raise_on_fail = raise_on_fail
        self.verbose = verbose

    """Writes timelines to csv file"""

    batchsize = 1000

    def run(self, *args, **kwargs):
        self.save(self, *args, **kwargs)

    def save(self, *args, **kwargs):
        """

        Parameters
        ----
        queries : string or dict
            The query to select elasticsearch records to export count.
            Also accepts a list of queries to create multiple comments
        destination : string (default: 'timeline_export.csv;')
            The destination to which to export records. 
        timefield : string (default: 'publication_date')
            The key to under which the date/time is stored
        granularity : string (default: 'week')
            The level of aggregation

        For more information, see analysis/timeline_analysis.py

        """
        outputfile = kwargs.pop("destination", "timeline_export.csv")
        queries = kwargs.pop("queries", "*")
        timefield = kwargs.pop("timefield", "publication_date")

        logger.info("Calling timeline generator...")
        timeline = timeline_generator()
        df = timeline.fit(queries=queries, timefield=timefield, **kwargs)

        logger.info("Saving timeline to {}".format(outputfile))
        df.to_csv(outputfile)
