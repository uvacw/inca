from lxml.html import fromstring as parser
from core.processor_class import Processer
from core.basic_utils import dotkeys
import logging

logger = logging.getLogger(__name__)

class xpath(Processer):
    '''Extract Xpath fields from html or xml documentsxs    '''

    def process(self, document_field, extract_dict, **kwargs):
        '''XPath-based extraction was applied to this document '''
        #logger.debug("field={field}, extract_dict={extract_dict}".format(**locals()))
        
        if type(extract_dict)==str:
            extract_dict = self._parse_strings_that_contain_dicts(extract_dict)
        try:
            parsed_document = parser(document_field)
        except:
            try:
                logger.info("attempting to process after utf-8 encoding")
                parsed_document = parser(document_field.encode('utf-8','replace'))
            except:
                logger.warning('failed to parse document! using xpath_parser, dict={extract_dict}'.format(**locals()))
        parsed_fields = parse_dict(parsed_document, extract_dict)
         
        return parsed_fields

def unlist(thing):
    outems = []
    for t in thing:
        if type(t)==list:
            outems.extend(unlist(t))
        else:
            outems.append(t)
    return outems

def parse_dict(dom, parsedict):
    '''
    This function parses xpaths from a DOM object iteratively based
    on a dictionary specification of extracted information.
    
    tuples: "for every element in xpath, parse value"
    dict  : "add key=DOM.xpath(value)"
    
    Example
    ---
    <speaker>
        <fn> Alice </fn>
        <gender> F  </gender>
    </speaker>
    <speaker>
        <fn> Bob </fn>
        <gender> M </gender>
    </speaker>

    becomes:
    { 'speakers' : [ 
    { 'fn' : 'Alice', 'gender' ; 'F' },
    { 'fn' : 'Bob', 'gender', 'M' }
    ] }

    using:
    
    { 'speakers' :  ('//speakers',{'fn':'.//fn', 'gender':'.//gender'})}
    '''
    if type(parsedict)==dict:
        return {k:parse_dict(dom,v) for k,v in parsedict.items()}
    elif type(parsedict)==tuple:
        listnode, elements = parsedict
        return [parse_dict(node, elements) for node in dom.xpath(listnode)]
    elif type(parsedict)==list:
        if len(parsedict)<1:
            return "None"
        if type(parsedict[0])==str or 'Unicode' in str(type(parsedict[0])):
            return ' '.join(parsedict)
        else:
            return ' '.join([e.text_content() for e in parsedict])
    elif type(parsedict)==str:
        return parse_dict(dom,dom.xpath(parsedict))
