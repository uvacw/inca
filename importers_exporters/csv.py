"""INCA CSV import & output functionality

This file contains the input/output functionality for '.csv' fiels INCA

"""

from core.import_export_classes import Importer, Exporter
from core.basic_utils import dotkeys
import csv
import chardet
import logging

logger = logging.getLogger(__name__)

class import_csv(Importer):
    """Read csv files"""

    def _detect_encoding(filename):
        try:
            with open(filename, mode='rb') as filebuf:
                encoding = chardet.detect(filebuf.peek(10000))
        except FileNotFoundError:
            logger.warning("File `{filename}` does not seem to exist".format(filename=filename))
            return False
        return encoding['encoding']

    def load(self, filename, fieldnames=None, *args, **kwargs):
        """Loads a csv file into INCA

        Parameters
        ----
        doctype : string
            Declares under which doctype the documents should be stored
        mapping : dict or None (default=None)
            A dictionary that specifies the from_key :=> to_key relation
            between loaded documents and documents as they should be indexed
            by elasticsearch.

            If 'None', takes the header of the file and uses these fieldnames
            to upload documents
        filename : string
            The file to load
        fieldnames : list or None
            If None, the first row is assumed to contain headers, else
            it should be a list that specifies, in order, columnnames.
        delimiter : string
            The character used to seperate columns, often ';', ',' or '\t'
        encoding ; string
            The encoding in which a file is, defaults to autodetect, but is also
            commonly 'UTF-16','ANSI','WINDOwS-1251'

        yields
        ---
        dict
            One dict per row of data in the excel file

        """
        encoding = kwargs.get('encoding',self._detect_encoding(filename))
        if encoding:
            with csv.DictReader(filename, encoding=encoding, *args, **kwargs) as csv_content:
                for row in csv_content:
                    yield row


class export_csv(Exporter):
    """Writes documents to csv file"""

    batchsize = 1000

    def save(self, documents, fields=None, include_meta=False):
        """

        Parameters
        ----
        query : string or dict
            The query to select elasticsearch records to export
        destination : string
            The destination to which to export records. If the subclass
            `to_file` property is set to `True`, a fileobject will be opened
            to that location.

            If the destination is a folder, a filename will be generated
        fields : list (default=None)
            Which fields to use in the output file. If `None`, all fields
            are used.
        include_meta : bool (default=False)
            Whether to include META fields.

        """
        if not hasattr(self, 'fields'):
            # keep track of fields
            self.fields = []

        flat_batch = map(self._flatten_doc, documents, include_meta)
        keys = set.union(*[set(d.keys()) for d in flat_batch])
        [self.fields.append(k) for k in keys if k not in self.fields]

        self.extension = ".csv"
        if  self.fileobj:
            outputfile = self.fileobj
            new = False
        else:
            outputfile = self._makefile(destination)
            new = True

        writer = csv.DictWriter(outputfile, self.fields, extrasaction='ignore',*args, **kwargs)
        if new:
            writer.writeheader()
        writer.writerows(flat_batch)
