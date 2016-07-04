from lxml.html import fromstring as parser
from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging

logger = logging.getLogger(__name__)

class xpath_processing(Processer):
    '''Extract Xpath fields from html or xml documents '''

    def process(self, document, field, extract_dict, **kwargs):
        '''XPath-based extraction was applied to this document '''
        if type(extract_dict)==str:
            extract_dict = self._parse_strings_that_contain_dicts(extract_dict)
        try:
            parsed_document = parser(dotkeys(document,field))
        except:
            logger.warning('failed to parse document {doc._id}! using xpath_parser, dict={extract_dict}'.format(**locals()))
        parsed_fields = dict()
        for fieldname, xpath in extract_dict.items():
            try:
                parsed_fields[fieldname] = parsed_document.xpath(xpath)
            except:
                logger.warning('failed to parse {fieldname}:{xpath} from {doc._id}'.format(**locals()))
        yield parsed_fields
