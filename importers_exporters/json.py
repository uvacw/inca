""" JSON dump importing and exporting functionality

JSON is a flexible and often used format to exchange data between web services,
think social media APIs (Twitter, Facebook,...) and web frameworks (Angular,
React). Elasticsearch uses it and MongoDB uses a dialect (BSON). This makes
JSON a nice and easy format for data exchange.

"""

from core.importers_exporters import Importer, Exporter
import os
import json
import zipfile
import gzip
import tarfile

class import_json(Importer):
    """imports json from from file(s)"""

    def _is_dir(self, filename):
        filename == os.path.join(os.dirname(filename),"")
        return True

    def _from_file(self, filename):
        yield

    def _from_dir(self, directory):
        yield

    def _detect_zip(self,path):
        filename = os.path.basename(path)
        for zip_ext in  ['zip','tar.gz','gz','bz2']:
            if filename[-len(zip_ext):] == zip_ext:
                return zip_ext
        return False

    def load(self, mapping, path, compress=""):
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

        """
