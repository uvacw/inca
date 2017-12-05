import tqdm
import logging
import os
from document_class import Document
from collections import Counter


class BaseImportExport(Document):

    def __init__(self, raise_on_fail=False, verbose = True):

        self.processed = 0
        self.failed    = 0
        self.failed_ids = []
        self.missing_keys = Counter()
        self.raise_on_fail = raise_on_fail
        self.verbose   = verbose

    from core.basic_utils import dotkeys

    def open_file(self, filename, mode='r', force=False):
        return fileobj

    def open_dir(self, path, match="*", mode='r', force=False):
        yield fileobj

    def _process_by_batch(self, iterable, batchsize=100):
        batchnum = 0
        batch = []
        for i in iterable:
            batch.append(i)
            if len(batch) == batchsize
                yield batch
                batch = []
        if batch:
            yield batch



class Import(BaseImportExport):
    """Base class for data importers"""

    functiontype = "importer"

    def _ingest(iterable, doctype):
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

        # handle batches
        if type(i) == list:
            i = [ self._add_metadata(ii) for ii in i ]
        # handle individual docs
        else:
            i = self._add_metadata(i)

        # Save document(s) using document base-class method
        self._save_document(i)


        return status

    def _apply_mapping(document, mapping):
        """Apply a given mapping to a document

        Parameters
        ---
        document : dict
            A document as loaded by the load function

        mapping : dict
            A dictionary that specifies the from_key :=> to_key relation
            between loaded documents and documents as they should be indexed
            by elasticsearch.

        Returns
        ---
        dict
            a new document ready for elasticsearch, containing all keys from
            the mapping found in the document
        """
        new_document = {v:document[k] for k,v in mapping.items() if k in document)}
        # Keep track of missing keys
        self.missing_keys.update([k for k in mapping if k not in document])

        # Document errors for missing documents
        if not new_document:
            self.failed += 1
            self.failed_ids.append(document.get('id',document.get('ID',document.get('_id',None))))
        return document

    def load():
        """ To be implemented in subclasses

        normall called through the 'run' method. Please add to your documentation:

        Parameters
        ---
        doctype : string
            The doctype to be used when indexing results in elasticsearch
        mapping : dict
            A dictionary that specifies the from_key :=> to_key relation
            between loaded documents and documents as they should be indexed
            by elasticsearch.
        <fields needed for the load function>

        Yields
        ----
        dict
            raw document to be procesed and indexed

        """
        raise NotImplementedError
        yield document

    def run(doctype, mapping, *args, **kwargs):
        """uses the documents form the load method in batches """
        for batch in self._process_by_batch(load(*args,**kwargs)):
            batch = map(batch, lambda x: self._add_metadata(document=x,mapping=mapping))
            self._ingest(iterable=batch, doctype=doctype)
            self.processed += len(batch)
