""" JSON dump importing and exporting functionality

JSON is a flexible and often used format to exchange data between web services,
think social media APIs (Twitter, Facebook,...) and web frameworks (Angular,
React). Elasticsearch uses it and MongoDB uses a dialect (BSON). This makes
JSON a nice and easy format for data exchange.

"""

from ..core.import_export_classes import Importer, Exporter, id2filename
import os
import json
import re
import logging
from glob import glob

logger = logging.getLogger("INCA." + __name__)


class import_json(Importer):
    """imports json from from file(s)"""

    version = 0.1

    def load(self, path, mapping={}, compression="autodetect", matches=".*"):
        """Load JSON objects from file or folder

        Parameters
        ---
        mapping : dict (default=None)
            A dictionary that specifies the from_key :=> to_key relation
            between loaded documents and documents as they should be indexed
            by elasticsearch.
            If `None` it imports json content as-is
        path : string
            The path to the content to load. If one file, this file is read
            line-by-line style. If it's a directory, each file there is read once.
        compression : string (default="autodetect")
            What compression was used to compress input file(s)
        matches : string (default='.*')
            Regular expression to match file. Helpful when a directory contains
            files that should not be loaded. Note: Ignored when open a single file

        """
        exists = os.path.exists(path)
        if not exists:
            logger.warning("Unable to open {path} : DOES NOT EXIST".format(path=path))
        else:
            is_dir = os.path.isdir(path)
            if not is_dir:
                list_of_files = glob(path)
            else:
                list_of_files = glob(path + "*.json")
            for item in list_of_files:
                with self.open_file(item, mode="r", compression=compression) as f:
                    line = "start"
                    while line:
                        line = f.readline()
                        if not line:
                            break
                        if type(line) != str:
                            line = line.decode()
                        doc = json.loads(line)
                        if doc:
                            yield doc.get("_source", doc)


class export_json_file(Exporter):
    """Dump documents to JSON file"""

    version = 0.1

    def save(
        self, batch_of_documents, destination, compression=None, include_meta=False
    ):
        """Save JSON objects to single file

        Parameters
        ---
        query : string or dict
            The query to select elasticsearch records to export
        destination : string
            The file in which to store the output
        compression : string (default=None)
            What compression to use when writing output file
        include_meta : Boolean (default=False)
            Whether to include META information. If set to False,
            Only the keys within the '_source' key will be saved
            and META will be excluded.
        """
        self.extension = "json"
        self.fileobj = self._makefile(destination, mode="at", compression=compression)
        for document in batch_of_documents:
            if include_meta == False:
                if "_source" in document.keys():
                    document = document["_source"]
                document = {k: v for k, v in document.items() if not k == "META"}
            try:
                doc_dump = json.dumps(document)
                self.fileobj.write(doc_dump + "\n")
            except:
                self.failed += 1
                self.failed_ids.append(document["_id"])
        if self.failed:
            logger.warning("Failed to export {num} documents".format(num=self.failed))
            logger.info("Failed ids: {ids}".format(ids=", ".join(self.failed_ids)))


class export_json_files(Exporter):
    """Dump documents to JSON files, one-per-document (NOT RECOMMENDED)"""

    version = 0.1

    def save(
        self, batch_of_documents, destination, compression=None, include_meta=False
    ):
        """Save JSON objects to multiple files

        Parameters
        ---
        query : string or dict
            The query to select elasticsearch records to export
        destination : string
            The directory in which to store the output files
        compression : string (default=None)
            What compression to use when writing output files
        include_meta : Boolean (default=False)
            Whether to include META information. If set to False,
            Only the keys within the '_source' key will be saved
            and META will be excluded.
        """
        self.extension = "json"
        for document in batch_of_documents:
            filename = id2filename(document.get("_id"))
            location = os.path.join(destination, filename)
            fileobj = self._makefile(location, mode="wt", compression=compression)
            if include_meta == False:
                if "_source" in document.keys():
                    document = document["_source"]
                document = {k: v for k, v in document.items() if not k == "META"}

            try:
                json.dump(document, fileobj)
            except:
                self.failed += 1
                self.failed_ids.append(document["_id"])
            fileobj.close()
        if self.failed:
            logger.warning("Failed to export {num} documents".format(num=self.failed))
            logger.info("Failed ids: {ids}".format(ids=", ".join(self.failed_ids)))
