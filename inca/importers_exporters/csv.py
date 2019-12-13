"""INCA CSV import & output functionality

This file contains the input/output functionality for '.csv' fiels INCA

"""

from ..core.import_export_classes import Importer, Exporter
from ..core.basic_utils import dotkeys
import csv
import chardet
import logging
import os
from glob import glob


logger = logging.getLogger("INCA")


class import_csv(Importer):
    """Read csv files"""

    version = 0.1

    def _detect_encoding(self, filename):
        try:
            with open(filename, mode="rb") as filebuf:
                encoding = chardet.detect(filebuf.peek(10000000))
        except FileNotFoundError:
            logger.warning(
                "File `{filename}` does not seem to exist".format(filename=filename)
            )
            return False
        return encoding["encoding"]

    def load(self, path, fieldnames=None, *args, **kwargs):
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
        path : string
            Either directory of files or file to load.
        fieldnames : list or None
            If None, the first row is assumed to contain headers, else
            it should be a list that specifies, in order, columnnames.
        delimiter : string
            The character used to seperate columns, often ';', ',' or '\t'
        encoding ; string
            The encoding in which a file is, defaults to 'utf-8', but is also
            commonly 'UTF-16','ANSI','WINDOwS-1251'. 'autodetect' will attempt
            to infer encoding from file contents

        yields
        ---
        dict
            One dict per row of data in the excel file

        """
        exists = os.path.exists(path)
        if not exists:
            logger.warning("Unable to open {path} : DOES NOT EXIST".format(path=path))
        else:
            is_dir = os.path.isdir(path)
            if not is_dir:
                list_of_files = glob(path)
            else:
                list_of_files = glob(path + "*.csv")
            for item in list_of_files:
                encoding = kwargs.pop("encoding", "utf-8")
                if encoding:
                    with open(item, encoding=encoding) as fileobj:
                        csv_content = csv.DictReader(fileobj, *args, **kwargs)
                        for row in csv_content:
                            for k in list(row):
                                if k.startswith("_source."):
                                    row[k[8:]] = row.pop(k)
                                elif k in ["_type", "_index"]:
                                    row.pop(k)
                                else:
                                    pass
                            try:
                                row["doctype"] = row["_source.doctype"]
                                yield row
                            except:
                                if "doctype" in row:
                                    yield row
                                else:
                                    logger.warning(
                                        "You need a key named 'doctype' to insert the document in the database"
                                    )


class export_csv(Exporter):
    """Writes documents to csv file"""

    batchsize = 1000

    def save(
        self,
        documents,
        destination,
        fields=None,
        include_meta=False,
        include_html=False,
        remove_linebreaks=True,
        *args,
        **kwargs
    ):
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
        include_html : bool (default=False)
            Whether to include HTML source.
        remove_linebreaks : bool (default=True)
            Replace line breaks within cells by a space

        args/kwargs are passed to csv.DictWriter.
        In particular, you might be interested in using the follwing arguments:

        delimiter=';'
            Use a semicolon instead of a comma. This is what Microsoft Excel
            expects in many locales (e.g., Dutch and German)

        """
        new = False
        if fields is None:
            fields = []
        self.fields = ["_source.{}".format(f) for f in fields]

        flat_batch = list(
            map(
                lambda doc: self._flatten_doc(doc, include_meta, include_html),
                documents,
            )
        )
        if len(self.fields) == 0:
            keys = set.union(*[set(d.keys()) for d in flat_batch])
            [
                self.fields.append(k)
                for k in keys
                if k not in self.fields and k != "_source.images"
            ]
            self.fields = sorted(self.fields)
        if new:
            logger.info("Exporting these fields: {}".format(self.fields))
        self.extension = "csv"

        if self.fileobj and not self.fileobj.closed:
            outputfile = self.fileobj
        elif self.fileobj:
            outputfile = self._makefile(destination, mode="a")
        else:
            outputfile = self._makefile(destination)
            new = True

        writer = csv.DictWriter(
            outputfile, self.fields, extrasaction="ignore", *args, **kwargs
        )
        if new:
            writer.writeheader()
        for doc in flat_batch:
            if remove_linebreaks:
                doc = {
                    k: v.replace("\n\r", " ").replace("\n", " ").replace("'r", " ")
                    for k, v in doc.items()
                }
            writer.writerow(doc)
