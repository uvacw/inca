#!/usr/bin/env python
'''
ooooo ooooo      ooo   .oooooo.         .o.       
`888' `888b.     `8'  d8P'  `Y8b       .888.      
 888   8 `88b.    8  888              .8"888.     
 888   8   `88b.  8  888             .8' `888.    
 888   8     `88b.8  888            .88ooo8888.   
 888   8       `888  `88b    ooo   .8'     `888.  
o888o o8o        `8   `Y8bood8P'  o88o     o8888o 
                                                  
Welcome to INCA

This module provides some data-scraping, searching and analysis functionality. 
You can run this locally, at a server, or perhaps on a cluster (hopefully) without too much
hassle.

Please consult the `README.md` file for more information about setting up and
running INCA. 

Start an API server:
        `inca` 

Commandline usage: 
        `inca <function> <task> <arguments>` 
Example: 
        `inca scrapers tweedekamer_handelingen run`

------------------------------------------------------------------------------
'''


from celery import Celery, group, chain, chord
from flask import Flask
import logging
import argparse
import core
import configparser
import core.search_utils
import core.taskmanager
import processing # helps celery recognize the processing tasks
import scrapers   # helps celery recognize the scraping tasks

config = configparser.ConfigParser()
try:    config.read_file(open('settings.cfg'))
except: print("settings.cfg is missing or corrupt!");exit()

LOCAL_ONLY = config.get('inca','local_only')=="True"

logger = logging.getLogger(__name__)
logging.basicConfig(level=config.get("inca","loglevel"))

api        = Flask(__name__)
taskmaster = Celery(
    backend = config.get('celery', '%s.backend' %config.get('inca','dependencies')),
    broker  = config.get('celery', '%s.broker' %config.get('inca','dependencies')),
)

taskmaster.conf.update(
    CELERYBEAT_SCHEDULE = core.celerybeat_schedule.get_scheduler()
)

expose = [ "scrapers", "processing", "analysis"]

@taskmaster.task
def run_scheduled(interval="all"):
    '''This task should be scheduled to run frequently!'''
    tasks = core.taskmanager.get_tasks(interval)
    logger.info("running schedule tasks for interval [{interval}]".format(**locals()))
    for taskname, task in tasks.items():
        taskname = task.get('name','UNKNOWN')
        logger.info("Running scheduled task [{taskname}]]".format(**locals()))
        if task.get('tasktype',"single") == "single":
            do(function=task['function'], task=task['task'],
                    *task['args'], **task['kwargs'])
        elif task.get('tasktype','single')=="batch":
            pass
    logger.info("Interval processed")


def show_functions():
    available_functions = """
    ---scrapers---   : 
        %s
        includes (`list` to see all options): %s
    ---processors--- : 
        %s
        includes (`list` to see all options): %s
    ---analysis---   : 
        %s
        includes (`list` to see all options): %s
    """ %(
        core.scraper_class.Scraper.__doc__,
        show_tasks('scrapers',3),
        core.processor_class.Processer.__doc__,
        show_tasks('processing',3),
        'ANALYSIS NOT IMPLEMENTED YET',
        'NO ANALYSIS TASKS AVAILABLE YET'
        )
    return available_functions

def show_tasks(function, limit=0):
    helpstring = "{function} provides the following tasks:\n\n".format(**locals())
    for function_task in [taskname for taskname in taskmaster.tasks if taskname.split('.')[0]==function]:
        taskdoc  = taskmaster.tasks[function_task].__doc__
        taskname = function_task.split('.')[-1]
        helpstring += "\t\t{taskname: <40} : {taskdoc}\n".format(**locals())
    return helpstring

def identify_task(function,task):
    if function not in expose:
        print("unknown function, please use one of the following:")
        print(show_functions())
    
    if task == "help": return "help"
    options = taskmaster.tasks.keys()
    fit     = [option for option in options if option.split('.')[0]==function and option.split('.')[-1]==task]
    if len(fit)==1:
        return fit[0]
    elif len(fit)<1:
        print("Did not find `{function}-{task}` ".format(**locals()))
        return "help"
    else:
        n_options = len(fit)
        print("found {n_options} for {function}/{task}!".format(**locals()))
        return "help"
    
def do(function, task, *args, **kwargs):
    ''' this handler function calls the appropriate celery task'''
    
    task_key = identify_task(function,task)
    logger.debug("running {function}:{task_key} with arguments {args}".format(**locals()))
    
    if task_key =='help':
        print(show_tasks(function))
    else:
        run_method = LOCAL_ONLY and 'run' or 'delay'
        result = getattr(taskmaster.tasks[task_key],run_method)(*args, **kwargs)
        return result

def group_do(query_or_list, function, task,field,force=False, skew=0, *args, **kwargs):
    '''
    input 
    --- 
    query_or_list: [ dict : elasticsearch query, list : set of documents or document_ids ]
    function : string
    task : specific task to use
    field : field of the document to process
    force (False): whether documents should be updated
    skew (0.0): delay between starting tasks (prevents overload of database)


    '''
    #if type(query_or_list)==list:
    #    documents = query_or_list
    #else:
    #   if not force:
    #        query_or_list.update({'filter':{'missing':{'field':'%s_%s' %(field,function)}}})
    #    documents = core.search_utils.scroll_query(query_or_list)
    documents = _doctype_query_or_list(query_or_list,force=force,field=field,function=task)
    return group(taskmaster.tasks[identify_task(function,task)].s(doc,field=field,force=force,*args,**kwargs) for
                 doc in documents).skew(step=skew).apply_async()

def batch_do(doctype_query_or_list, function, task, field, force=False, bulksize=50, *args, **kwargs):
    """
    Applies a function:task combination to all documents given, but saves them in batches to avoid overloading the database.
    """
    documents = _doctype_query_or_list(doctype_query_or_list, force=force, field=field, function=function)
    batchjobs = []
    for batch in _batcher(documents, batchsize=bulksize):
        if not batch: continue #ignore empty batches
        batch_tasks = [taskmaster.tasks[identify_task(function, task )].s(document=doc,field=field,
                                                                          force=force, *args, **kwargs)
                       for doc in batch]
        batch_chord = chord(batch_tasks)
        batch_result= batch_chord(taskmaster.tasks['core.database.bulk_upsert'].s())
        batchjobs.append(batch_result)
    return group(batch.s() for batch in batchjobs)

def _doctype_query_or_list(doctype_query_or_list,force=False, field=None, function=None):
    if type(doctype_query_or_list)==list:
        documents = doctype_query_or_list
    elif type(doctype_query_or_list)==str:
        if force or not field:
            documents = core.database.scroll_query({'filter':{'match':{'_type':doctype_query_or_list}}})
        elif not force and field:
            documents = core.database.scroll_query({'query':{'match':{'doctype':doctype_query_or_list}},
                                                    'filter':{'missing':{'field': '%s_%s' %(field,function) }}})
    else:
        if not force and field and function:
            doctype_query_or_list.update({'filter':{'missing':{'field':'%s_%s' %(field,function)}}})
        documents = core.search_utils.scroll_query(doctype_query_or_list)
    return documents        

def _batcher(stuff, batchsize=10):
    batch = []
    for num,thing in enumerate(stuff):
        batch.append(thing)
        if (num+1) % batchsize == 0:
            logger.info('processing batch %s' %(num+1))
            yield_batch = batch
            batch = []
            yield yield_batch
    if batch:
        yield batch 

   
if __name__ == '__main__':

    # prints the banner
    print(__doc__)

    # Parses options
    parser = argparse.ArgumentParser()
    parser.add_argument('function',      help="functions performed by INCA", default=False, nargs="?")
    parser.add_argument('task',          help="a task to be preformed such as tokenizing, expanding urls...", default='help', nargs="?")
    parser.add_argument('task_args',     help='arguments passed to task (not all tasks take arguments!)', nargs='*')
    parser.add_argument('-p','--port',   help='set port for api server', default=5000, type=int)
    parser.add_argument('-d','--debug',  help='override config to set debug to true', action="store_true")
    parser.add_argument('--logfile',     help='override config for logfile use and location', default=None)
    parser.add_argument('-l', '--local', help='override config for local execution', action='store_true')
    
    args = parser.parse_args()

    # Handle some general override arguments for logging
    if args.debug:   print("OVERRIDE LOGLEVEL")
    if args.logfile: print("OVERRIDE LOGFILE TO {args.logfile}".format(**locals()))

    logging.basicConfig(level=args.debug and logging.DEBUG or LOGLEVEL,
                        filename=args.logfile,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )

    # Basic Celery override
    if args.local:
        LOCAL_ONLY = False

    # Run appropriate commands
    if not args.function:
        # run API server
        api.run()

    if args.function=='list':
        print(show_functions())
    else:
        do(args.function, args.task, args.task_args)
    
 
