"""
This file contains functionality to repair errors in the database,
for instance to re-parse the raw html source and/or to re-download
the HTML source
"""

from ..core.processor_class import Processer
from ..core.database import update_document, get_document, check_exists
from dateutil import parser
import datetime
import logging

logger = logging.getLogger("INCA")
logger.setLevel("DEBUG")


class reparse(Processer):
    """
    Sometimes, content is not correctly parsed, because a scraped site
    might have changed their layout. This allows to re-parse content
    by specifiying the new function to parse the content
    """

    def process(self, document_field, parsefunction, **kwargs):
        """
        Takes a document and a parsing function and re-parses the HTML source.

        Parameters
        ---
        docuent_field: string
            HTML source to be parsed

        parsefunction
            a Python function to parse the HTML source


        Example
        ---
        p = inca.processing.repair_processing.reparse()
        p.run('https://www.nu.nl/-/4959386/','htmlsource',parsefunction=inca.scrapers.news_scraper.nu.parsehtml, save=True, Force=True)
    
        """

        newfields = parsefunction(self, htmlsource=document_field)
        return newfields


class redownload(Processer):
    """
    Sometimes, content is not correctly downloaded, for instance due to
    a new cookie wall. This allows to re-download the content
    by specifiying the new function to download the content
    """

    def process(
        self, document_field, downloadfunction, linkpreprocessor=None, **kwargs
    ):
        """
        Takes a document and a parsing function and re-parses the HTML source.

        Parameters
        ---
        docment_field: string
            URL to be re-downloaded
        downloadfunction
            a Python function to download the URL

        Example
        ---
        p = inca.processing.repair_processing.reparse()
        p.run('https://www.nu.nl/-/4959386/','url',downloadfunction=inca.scrapers.news_scraper.nu.get_page_body)
    
        """
        if linkpreprocessor is None:
            link = document_field
        else:
            link = linkpreprocessor(self, document_field)
        newdownload = downloadfunction(self, link)
        return newdownload
