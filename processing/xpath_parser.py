from lxml.html import fromstring as html_parser
#from lxml.xml  import fromstring as xml_parser
from core.processor_class import Processer
from core.utils import dotkeys
import logging

logger = logging.getLogger(__name__)

class xpath_processors(Processer):
    '''Extract Xpath fields from html or xml documents '''

    def process(self, document, field, extract_dict, **kwargs):
        '''XPath-based extraction was applied to this document '''
        
        try:
            parsed_document = html_parser(dotkeys(document,field))
        except:
            logger.warning('failed to parse document {doc._id}! using xpath_parser, dict={extract_dict}'.format(**locals()))
        parsed_fields = dict()
        for fieldname, xpath in extract_dict.items():
            try:
                parsed_fields[fieldname] = parsed_document.xpath(xpath)
            except:
                logger.warning('failed to parse {fieldname}:{xpath} from {doc._id}'.format(**locals()))
        yield parsed_fields
