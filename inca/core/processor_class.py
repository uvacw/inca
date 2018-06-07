'''

This file contains the class for processor scripts. Processors
should take a document id list or iterable as input and add a new key:value pair (with
corresponding metadata).

the <function>_processing class should have a `process` method that
yields a key:value pair per document, but does not need to return the old document
(the old document will simple be expanded).

'''

import logging
from .document_class import Document
from .database import get_document, update_document, check_exists, config, check_mapping
# from . import *

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class Processer(Document):
    '''
    Processors change individual documents, for example by tokenizing, lemmatizing
    parsing XML sources etcetera.

    Make processers in the 'processers' folder by using <datasource>_processer.py as
    the filename, containing a class which inherits from this class.

    '''

    functiontype = 'processing'

    def __init__(self, test=True, async=True):
        '''Override test to save results and return an ID list instead of updated documents'''
        self.test  = test
        self.async = async

    def _test_function(self):
        '''OVERWRITE THIS METHOD, should yield True (if it works) or False (if it doesn't) '''
        return {self.__name__ : {'status':False, 'message':'UNKNOWN' }}

    def process(self, document_field, *args, **kwargs):
        '''CHANGE THIS METHOD, should return the changed document'''
        return updated_field

    def runwrap(self, docs_or_query,field,force=False, action='run' , *args, **kwargs):
        '''
        Run a processor by supplying a list of documents, a query or a doctype .
        Actions specify the way in which the task should be run.

        Input
        ---
        docs_or_query:
            either a list of documents, an elasticsearch query or a string specifying the doctype
        action: on of ['run','delay', 'batch' ]

        '''
        documents = _doctype_query_or_list(docs_or_query,field=field, force=force)

        if action == 'run':
            for doc in documents:
                yield self.run(doc, field, *args, **kwargs)

        elif action == 'delay':
            for doc in documents:
                for placeholder in self.delay(doc,*args,**kwargs):
                    yield placeholder
        elif action == 'batch':
            for num, batch in enumerate(_batcher(documents, batchsize=bulksize)):
                core.database.bulk_upsert().run(documents=[target_func.run(document=doc,
                                        field=field, force=force, *args, **kwargs) for
                                       doc in batch ] )
                now = datetime.datetime.now()
                logger.info("processed batch {num} {now}".format(**locals()))
                yield batch


        elif action == 'celery_batch':
            for batch in _batcher(documents, batchsize=bulksize):
                if not batch: continue #ignore empty batches
                batch_tasks = [target_func.s(document=doc,field=field,
                                            force=force, *args, **kwargs)
                               for doc in batch]
                batch_chord = chord(batch_tasks)
                batch_result= batch_chord(taskmaster.tasks['core.database.bulk_upsert'].s())
                yield batch




    def run(self, document,field,new_key=None,save=False, force=False, *args, **kwargs):
        '''
        Run a processor.

        Input
        ---
        document: dict or str
            document to be processed
        field: str
            key of the field to be processed
        new_key: str
            if specified, this key will be used as name for new field (instead of field_processorname)
        save: boolean
            indicates whether the result will be stored in the database
        force:
            indicates whether the document should replace (true) or only
            expand existing documents (false). Note that partial updates
            are not supported when forcing.
        '''

        # 1. check if document or id --> return do
        #print(document)
        #print(type(document))
        logger.debug("trying to process: ",document)
        masked = False # expect a document to be processed as-is (assumes ES origin)
        if not (type(document)==dict):
            logger.debug("input not a document")
            if field==None: # This path is used to run examples (ignores save)
                return self.process(document, *args, **kwargs)
            elif check_exists(document):
                document = get_document(document)
            else:
                logger.debug("document retrieval failure {document}".format(**locals()))
                return document
        if not "_source" in document:
            masked = True #mask documents to ES expectations
            document = {'_source':document}
        if not new_key:
            new_key =  "%s_%s" %(field, self.__name__)
        # 2. check whether processing can be skipped
        if not force and new_key in document['_source'].keys(): return document
        # 3. return None if key is missing
        if not field in document['_source'].keys():
            print(document['_source'].keys())
            logger.warning("Key not found in document")
            if masked:
                document = document['_source']
            return document
        # 4. process document
        document['_source'][new_key] = self.process(document['_source'][field], *args, **kwargs)
        # 3. add metadata
        # document['_source'] = self._add_metadata(document['_source'])
        # 4. check metadata
        # self._verify(document['_source'])
        # 5. save if requested
        if save:
            #print('ABOUT TO SAVE')
            #print(document)
            update_document(document, force=force)
        # 6. emit dotkey-field
        if masked:
            document = document['_source']
        return document


def _doctype_query_or_list(doctype_query_or_list, force=False, field=None, task=None):
    '''
    This function helps other functions dynamically interpret the argument for document selection.
    It allows for either a list of documents, an elasticsearch query, a string-query or a doctype
    string to be provided and returns an iterable containing these documents.

    Parameters
    ----------
    doctype_query_or_list: list, string or dict
        specification of input document, either:
            a list, each element should be an elasticsearch document
            a dict, should be an elasticsearch query
            a string, which is either an exact match with doctype (checked against doctype mappings) or
                alternatively, a query_string for the elasticsearch database
    force: bool (defautl=False)
        whether existing fields should be re-computed. Used to subset to documents were field is missing.
    field: string (default=None)
        Field on which operations are done, used to check when force=False
    task: string (default=None)
        Function for which the documents are used. Argument is used only to generate the expected outcome
        fieldname, i.e. <field>_<function>

    Returns
    -------
    Iterable
    '''

    if type(doctype_query_or_list)==list:
        documents = doctype_query_or_list
    elif type(doctype_query_or_list)==str:
        if doctype_query_or_list in core.database.client.indices.get_mapping()[config.get('elasticsearch','document_index')]['mappings'].keys():
            logger.info("assuming documents of given type should be processed")
            if check_mapping(doctype_query_or_list) == "mixed_mapping": 
                doctypefield = "doctype.keyword"
            elif check_mapping(doctype_query_or_list) == "new_mapping": 
                doctypefield = "doctype"
            elif check_mapping(doctype_query_or_list) == None: 
                raise()
            if force or not field:
                documents = core.database.scroll_query({'query':{'match':{doctypefield:"%s"%doctype_query_or_list}}})
            elif not force and field:
                logger.info("force=False, ignoring documents where the result key exists (and has non-NULL value)")
                #documents = core.database.scroll_query(
                #    {'filter':{'and': [
                #            {'match':{doctypefield:doctype_query_or_list}},
                #            {'missing':{'field': '%s_%s' %(field, task)}}]
                #               }})
                q = {"query":
                            {
                            "bool":
                                {'must_not':
                                     {
                                    'exists':{'field':'{}_{}'.format(field,task)}}, 
                            "filter":
                                {
                                "term" : {
                                    doctypefield : doctype_query_or_list
                                    }
                                }
                            }}}
                logger.debug(q)
                documents = core.database.scroll_query(q)


        else:
            logger.info("assuming input is a query_string")
            if force or not field:
                documents = core.database.scroll_query({'query':{'query_string':{'query': doctype_query_or_list}}})
            elif not force and field:
                logger.info("force=False, ignoring documents where the result key exists (and has non-NULL value)")
                #documents = core.database.scroll_query({'query':{'and':[
                #    {'missing':{'field':'%s_%s' %(field, task)}},
                #    {'query_string':{'query':doctype_query_or_list}}
                #]}})
                documents = core.database.scroll_query({'query':{'query_string':{'query': "({}) AND NOT _exists_:{}_{}".format(doctype_query_or_list,field,task)}}})

    else:
        if not force and field and task and not doctype_query_or_list:
            field = '%s_%s' %(field, task)
            doctype_query_or_list.update({'query':{'missing':{'field':field}}})
        documents = core.database.scroll_query(doctype_query_or_list)
    return documents

def _batcher(stuff, batchsize=10):
    batch = []
    for num,thing in enumerate(stuff):
        batch.append(thing)
        if (num+1) % batchsize == 0:
            logger.debug('processing batch %s' %(num+1))
            yield_batch = batch
            batch = []
            yield yield_batch
    if batch:
        yield batch
