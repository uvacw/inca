import tqdm
import logging
import os
import time
from .document_class import Document
from collections import Counter
from .search_utils import document_generator
from .filenames import id2filename
import zipfile
import gzip
import tarfile
import bz2
import os
import re

logger = logging.getLogger("INCA:" + __name__)


class BaseImportExport(Document):
    def __init__(self, raise_on_fail=False, verbose=True):

        self.processed = 0
        self.failed = 0
        self.failed_ids = []
        self.missing_keys = Counter()
        self.raise_on_fail = raise_on_fail
        self.verbose = verbose

    from .basic_utils import dotkeys

    def _detect_zip(self, path):
        filename = os.path.basename(path)
        for zip_ext in ["gz", "bz2"]:
            if filename[-len(zip_ext) :] == zip_ext:
                return zip_ext
        return False

    def open_file(self, filename, mode="r", force=False, compression="autodetect"):
        if mode not in ["w", "wb", "wt", "a", "ab", "at"] and not os.path.exists(
            filename
        ):
            logger.warning("File not found at {filename}".format(filename=filename))
        if compression == "autodetect":
            compression = self._detect_zip(filename)
        if not compression:
            return open(filename, mode=mode)
        else:
            filename += "." + compression

        if compression == "gz":
            return gzip.open(filename, mode=mode)
        if compression == "bz2":
            return bz2.open(filename, mode=mode)
        return fileobj

    def open_dir(
        self, path, mode="r", match=".*", force=False, compression="autodetect"
    ):
        """Generator that yields all files in given directory

        Parameters
        ----
        path : string
            A path in which to look for files
        mode : string (default='r')
            The mode to open files, such as `r` for reading UTF-8, `w` to write
        match : string (default='.*')
            a regular expression to match to filenames
        force : bool (default=False)
            Whether to return files for writing if they already exist
        compression : string (default="autodetect")
            Type of compression to use


        """
        matcher = re.compile(match)
        for filename in os.listdir(path):
            # ignore non-matching filenames
            if not matcher.search(filename):
                continue
            fileobj = self.open_file(
                os.path.join(path, filename),
                mode=mode,
                force=force,
                compression=compression,
            )
            yield fileobj

    def _process_by_batch(self, iterable, batchsize=100):
        batchnum = 0
        batch = []
        for i in iterable:
            batch.append(i)
            if len(batch) == batchsize:
                yield batch
                batch = []
        if batch:
            yield batch


class Importer(BaseImportExport):
    """Base class for data importers"""

    functiontype = "importer"

    def _ingest(self, iterable, doctype):
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
        if type(iterable) == list:
            i = [self._add_metadata(ii.get("_source", ii)) for ii in iterable]
        # handle individual docs
        else:
            i = self._add_metadata(iterable.get("_source", iterable))

        # Save document(s) using document base-class method
        self._save_document(i)

    def _apply_mapping(self, document, mapping):
        """Apply a given mapping to a document

        Parameters
        ---
        document : dict
            A document as loaded by the load function

        mapping : dict
            A dictionary that specifies the from_key :=> to_key relation
            between loaded documents and documents as they should be indexed
            by elasticsearch.

            If mapping is empty, the file contents are assumed to be ingested
            as is.

        Returns
        ---
        dict
            a new document ready for elasticsearch, containing all keys from
            the mapping found in the document
        """
        if not mapping:
            return document
        new_document = {v: document[k] for k, v in mapping.items() if k in document}
        # Keep track of missing keys
        self.missing_keys.update([k for k in mapping if k not in document])

        # Document errors for missing documents
        if not new_document:
            self.failed += 1
            self.failed_ids.append(
                document.get("id", document.get("ID", document.get("_id", None)))
            )
        return new_document

    def load(self):
        """ To be implemented in subclasses

        normally called through the 'run' method. Please add to your documentation:

        Parameters
        ---
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

    def run(self, mapping={}, *args, **kwargs):
        """uses the documents from the load method in batches """
        self.processed = 0
        for batch in self._process_by_batch(self.load(*args, **kwargs)):
            batch = list(map(lambda doc: self._apply_mapping(doc, mapping), batch))
            for doc in batch:
                self._ingest(iterable=doc, doctype=doc["doctype"])
                self.processed += 1
        logger.info("Added {} documents to the database.".format(self.processed))


class Exporter(BaseImportExport):
    """Base class for exporting"""

    # set to_file to `False` for subclasses that do not export to files
    # for instance when writing to external databases
    to_file = True
    batchsize = 100

    def __init__(self, *args, **kwargs):
        BaseImportExport.__init__(self, *args, **kwargs)
        self.fileobj = None
        self.extension = ""

    def save(self, batch_of_documents, destination="exports", *args, **kwargs):
        """To be implemented in subclass

        This method should process batches of documents by exporting them in
        whatever format implemented in the exporter.

        Parameters
        ----
        batch_of_documents : list of dicts
            a list containing the dict of each document as represented in
            elasticsearch

        ...<arguments specific to exporter>

        """
        raise NotImplementedError

    def _flatten_doc(self, document, include_meta=False, include_html=False):
        """Utility to convert elasticsearch documents to a flat representation

        Parameters
        ---
        document : dict
            A dictionary which may include nested fields

        Returns
        ----
        dict
            A dictionary where values are all strings, Nested keys are
            merged by '.'

        """
        flat_dict = {}
        for k, v in document.items():
            if k == "META" and not include_meta:
                continue
            if k == "htmlsource" and not include_html:
                continue
            if type(v) == str:
                flat_dict[k] = v
            elif type(v) == list:
                flat_dict[k] = str(v)
            elif type(v) == dict:
                for kk, vv in self._flatten_doc(v).items():
                    flat_dict["{k}.{kk}".format(k=k, kk=kk)] = vv
            else:
                try:
                    flat_dict[k] = str(v)
                except:
                    logger.warning("Unable to ready field {k} for writing".format(k=k))
        return flat_dict

    def _retrieve(self, query):
        for doc in document_generator(query):
            self.processed += 1
            yield doc

    def _makefile(self, filename, mode="wt", force=False, compression=False):
        filepath = os.path.dirname(filename)
        os.makedirs(filepath, exist_ok=True)
        # handle cases when a path instead of a filename is provided
        if os.path.isdir(filename):
            now = time.localtime()
            newname = "INCA_export_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}.{extension}".format(
                now=now, extension=self.extension
            )
            filename = os.path.join(filename, newname)
        if self.extension not in filename:
            filename = "{filename}.{extension}".format(
                filename=filename, extension=self.extension
            )
        if filename in os.listdir(filepath) and not force:
            logger.warning(
                "file called {filename} already exists, either provide new filename"
                "or set `overwrite=True`".format(filename=filename)
            )
            return False
        else:
            self.fileobj = self.open_file(
                filename, mode=mode, force=force, compression=compression
            )
            return self.fileobj

    def run(
        self,
        query="*",
        destination="exports/",
        overwrite=False,
        batchsize=None,
        *args,
        **kwargs
    ):
        """Exports documents from the INCA elasticsearch index

        DO NOT OVERWRITE

        This method is the common-caller for the exporter functionality. Common
        functionality such as passing the query to ES, retrieving documents,
        making sure a file exists. The `save` method should implement a
        batch-wise handling of elasticsearch documents, for instances by
        writing them to a file.

        Parameters
        ---
        query : string or dict
            The query to select elasticsearch records to export
        destination : string
            The destination to which to export records. If the subclass
            `to_file` property is set to `True`, a fileobject will be opened
            to that location.

            If the destination is a folder, a filename will be generated.

            Filenames are generated with extensions declared in 'self.extention'
        overwrite : bool (default=False)
            Whether to write over an existing file (stop if False)
        batchsize : int
            Size of documents to keep in memory for each batch
        *args & **kwargs
            Subclass specific arguments passed to save method

        """
        if not batchsize:
            batchsize = self.batchsize
        for docbatch in self._process_by_batch(
            self._retrieve(query), batchsize=batchsize
        ):
            self.save(docbatch, destination=destination, *args, **kwargs)
        if self.fileobj:
            self.fileobj.close()
