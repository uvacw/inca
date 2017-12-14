""" JSON dump importing and exporting functionality

JSON is a flexible and often used format to exchange data between web services,
think social media APIs (Twitter, Facebook,...) and web frameworks (Angular,
React). Elasticsearch uses it and MongoDB uses a dialect (BSON). This makes
JSON a nice and easy format for data exchange.

"""

from core.importers_exporters import Importer, Exporter
import os
import json
import re


class import_json(Importer):
    """imports json from from file(s)"""


    def load(self, path, mapping=None, compression="autodetect", matches=".*"):
        """Load JSON objects from file or folder

        Parameters
        ---
        doctype : string
            The doctype to be used when indexing results in elasticsearch
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
        exists  = os.path.exists(path)
        if not exists:
            logger.warning("Unable to open {path} : DOES NOT EXIST".format(path=path))
        else:
            is_path = os.path.isdir(path)
            if not is_path :
                with self.open_file(path, mode=mode, compression=compression) as f:
                    line = "start"
                    while line:
                        line = f.readline()
                        if type(line)!=str:
                            line = line.decode()
                        doc = json.loads(doc)
                        if doc:
                            yield doc
            if is_path:
                matcher = re.compile(matches)
                for filename in os.listdir(path):
                    if not matcher.search(filename): continue
                    yield self.load(os.path.join(path,filename), mapping=mapping, compression=compression)

class export_json(Exporter):
    """Dump documents to JSON file(s)"""

    extension = ".json"

    def save(self, documents, path):
        pass
