'''
This file contains some recoding options, such as string-to-date,
field-to-field etcetera.
'''

from ..core.processor_class import Processer
from ..core.database import update_document, get_document, check_exists
from dateutil import parser
import datetime
import logging

logger = logging.getLogger("INCA")

class datetime_string_to_date(Processer):
    '''
    Takes a specified date-format and outputs ISO-datetimes

    Parameters
    ---
    Document_field: string
        string that should be parsed
    input_format: string
        string with parsing schema, consistent with datetime expectations

    Output
    ---
    Datetime object

    Example
    ---
    document_field = 'Fri Jun 10 19:27:13 +0000 2016'
    input_format   = "%a %b %d %H:%M:%S %z %Y"

    output : datetime.datetime(2016, 6, 10, 19, 27, 13, tzinfo=datetime.timezone.utc)

    Notes
    ---
    MAY NOT WORK for timezone parsing...

    See Also: https://docs.python.org/2/library/datetime.html

    '''

    def process(self, document_field, input_format):
        '''standardized datetime format'''
        return datetime.datetime.strptime(document_field,input_format)

class dateutil_string_to_date(Processer):
    '''
    Takes strings and returns datetime objects based on dateutil parsing.


    Parameters
    ----------
    document_field: string
        string that should be parsed
    year_first: bool (default=False)
        whether ambiguous strings (12/06/13) should be interpreted as year
        first. (i.e. 2012 june 13 instead of 2013 june 12)
    day_first: bool (default=False)
        Whether ambiguous strings should be interpreted as day_first.
    fuzzy: bool (default=True)
        Allows for fuzzy matching
    kwargs:
        keyword arguments to pass to dateutil.parser.parse

    Returns
    -------
        Datetime
    '''

    def process(self, document_field, year_first=False, day_first=False, fuzzy=False, **kwargs):
        '''Extracted datetime from string'''
        return parser.parse(document_field, yearfirst=year_first,
                            dayfirst=day_first, fuzzy=fuzzy, **kwargs)

class rename_field(Processer):
    '''
    Sometimes fields from different collections may have identical content, but
    different names. E.g. 'publicationDate', 'post Date' and 'Date posted'. This
    processer recodes fields to reflect new fields.
    '''

    def process(self, document,  old_field, new_field, project='default'):
        '''names {new_field} from {old_field}'''.format(**locals())
        pass

    def run(self, document, field, new_field, save=False, force=False):
        old_field = field

        logger.debug("tring to process: ", document)
        if not (type(document) == dict and '_source' in document.keys()):
            logger.debug("input not a document")
            if check_exists(document):
                document = get_document(document)
            else:
                logger.debug("document retrieval failure {document}".format(**locals()))
                return document

        if old_field not in document['_source'].keys():
            logger.debug("Source field missing: ignoring rename")
            return document

        elif new_field in document['_source'].keys() and new_field in document['_source']['META'].keys():
            logger.info("Existing *original* (non moved) field: ignoring rename!")
            return document

        elif not new_field in document['_source'].keys():
            document['_source'][new_field] = document['_source'][old_field]
            document['_source']['META'][new_field] = document['_source']['META'][old_field]
            document['_source']['META'][new_field]['moved_from'] = old_field

        elif 'moved_from' in document['_source']['META'].keys():
            logger.info("Moving to existing field (which was itself a result of moving)")
            document['_source'][new_field] = document['_source'][old_field]
            document['_source']['META'][new_field] = document['_source']['META'][old_field]
            document['_source']['META'][new_field]['MOVED_FROM'] = old_field


        self._verify(document['_source'])
        if save: update_document(document, force=True)
        return document
