import tqdm
import logging
import os
from document_class import Document


class BaseImportExport(Document):

    def __init__(self, raise_on_fail=False, verbose = True):

        self.processed = 0
        self.failed    = 0
        self.failed_ids = []
        self.raise_on_fail = raise_on_fail
        self.verbose   = verbose

    from core.basic_utils import dotkeys

    def open_file(self, filename, mode='r', force=False):
        return fileobj

    def open_dir(self, path, match="*", mode='r', force=False):
        yield fileobj

    def _process_by_batch(self, iterable, function, batchsize=100):
        batchnum = 0
        batch = []
        for i in iterable:
            batch.append(i)
            if len(batch) == batchsize
                function(batch)
                batch = []
        if batch:
            function(batch)



class Import(BaseImportExport):
    """Base class for data importers"""

    functiontype = "importer"

    def ingest(iterable, doctype):
        """Ingest document (batch)

        Parameters
        ----
        iterable : iterable
            A list, generator or other iterable that yields documents or
            batches of documents to be stored in elasticsearch. This method
            should be called from the `load` method implemented in a specific
            importer

        doctype : string
            A string to set the doctype of the added documents

        """
        self.doctype = doctype
        for i in iterable:
            # handle batches
            if type(i) == list:
                i = [ self._add_metadata(ii) for ii in i ]
            # handle individual docs
            else:
                i = self._add_metadata(i)

            # Save document(s) using document base-class method
            self._save_documents(i)


        return status
