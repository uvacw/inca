'''
This file contains some recoding options, such as string-to-date,
field-to-field etcetera.
'''

from core.processor_class import Processer
import datetime

class string_to_date(Processer):
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
    See Also: https://docs.python.org/2/library/datetime.html

    '''

    def process(self, document_field, input_format):
        '''standardized datetime format'''
        return datetime.datetime.strptime(document_field,input_format)

