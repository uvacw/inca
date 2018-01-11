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
'''

import os
import logging
import inspect


logging.basicConfig(level="WARN")
logger = logging.getLogger("INCA")


if not 'settings.cfg' in os.listdir('.'):
    logger.info('No settings found, applying default settings (change in `settings.cfg`)')
    from shutil import copyfile
    copyfile('default_settings.cfg','settings.cfg')

from celery import Celery, group, chain, chord
import core
import configparser
import core.search_utils
import core.taskmanager
import datetime
import processing # helps celery recognize the processing tasks
import scrapers   # helps celery recognize the scraping tasks
import clients    # helps celery recognize client tasks
import analysis   # helps celery recognize analysis tasks
from optparse import OptionParser

from core.database import config


class Inca():
    """INCA main class for easy access to functionality

    methods
    ----
    Scrapers
        Retrieval methods for RSS feeds and websites. Most scrapers can run
        out-of-the-box without specifying any parameters. If no database is
        present, scrapers will return the data as a list.

        usage:
            docs = inca.scrapers.<scraper>()
    Clients
        API-clients to get data from various endpoints. You can start using client
        functionality by:
        1) Adding an application, using the `<service>_create_app` method
        2) Add credentials to that application, using `<service>_create_credentials`
        3) Then run a collection method, such as `twitter_timeline`!

        usage:
            inca.clients.<service>_create_app(name='default')
            inca.clients.<service>_create_credentials(app='default')
            docs = inca.clients.<service>_<functionname>(app='default', *args, **kwargs)

    Processing
        These methods change documents by adding fields. Such manipulations can
        be things such as POS-tags, Sentiment or something else.

        usage:
            modified_docs = inca.processing.<processor>(docs=<original_docs or query>, field=<field to manipulate>, *args, **kwargs)


    """

    _taskmaster = Celery(
        backend = config.get('celery', '%s.backend' %config.get('inca','dependencies')),
        broker  = config.get('celery', '%s.broker' %config.get('inca','dependencies')),
    )

    database = core.search_utils

    def __init__(self, distributed=False):
        self._LOCAL_ONLY = distributed
        self._construct_tasks('scrapers')
        self._construct_tasks('processing')
        self._analysis_task_constructor()

    class scrapers():
        '''Scrapers for various (news) outlets '''
        pass

    class processing():
        '''Processing options to operate on documents'''
        pass

    class analysis():
        '''Perform and summarize analysis done on documents'''
        pass

    def _analysis_task_constructor(self):
        """Construct endpoints specifically for analysis tasks

        This function is used when analysis tasks are encountered. The Analysis
        sub-classes include functionality for fitting, predicting, plotting,
        updateing and explaining results.

        """

        target_functions = ['fit','predict','plot','interpretation','quality']

        for k,v in self._taskmaster.tasks.items():
            functiontype = k.split('.',1)[0]
            taskname     = k.rsplit('.',1)[1]
            if functiontype == "analysis":

                analysis_class = self._taskmaster.tasks[k]

                def makefunc(method):
                    if inspect.isgeneratorfunction(method):
                        def endpoint(*args, **kwargs):
                            for i in method(*args, **kwargs):
                                yield i
                    else:
                        def endpoint(*args, **kwargs):
                            return method(*args, **kwargs)
                    return endpoint

                class analysis_placeholder:
                    pass
                analysis_placeholder.__doc__ = analysis_class.__doc__

                for method in target_functions:
                    endpoint = getattr(analysis_class,method)
                    setattr(analysis_placeholder,method,endpoint)

                setattr(getattr(self,"analysis"), taskname, analysis_placeholder)

    def _construct_tasks(self, function):
        """Construct the appropriate endoints from Celery tasks

        This function serves to create the appropriate functions in the Inca
        object by intro-specting available functions from the celery taskmaster.
        Subclasses of Task should then be added automatically.

        Parameters
        ----
        function : string
            The type of function to add, such as 'scrapers' or 'processors'

        Returns
            None


        """
        for k,v in self._taskmaster.tasks.items():
            functiontype = k.split('.',1)[0]
            taskname     = k.rsplit('.',1)[1]
            if functiontype == function:
                function_class = getattr(self,function)
                leaf_class = self._taskmaster.tasks[k]
                method = leaf_class.runwrap
                def makefunc(method):
                    if inspect.isgeneratorfunction(method):
                        def endpoint(*args, **kwargs):
                            for i in method(*args, **kwargs):
                                yield i
                    else:
                        def endpoint(*args, **kwargs):
                            return method(*args, **kwargs)
                    return endpoint

                endpoint = makefunc(method)
                if function == 'scrapers':
                    docstring = self._taskmaster.tasks[k].get.__doc__
                elif function == "processing":
                    docstring = self._taskmaster.tasks[k].process.__doc__
                else:
                    docstring = self._taskmaster.tasks[k].__doc__
                endpoint.__doc__  = docstring
                endpoint.__name__ = leaf_class.__name__

                setattr(function_class,taskname,endpoint)



    def _summary(self):
        summary = ''
        summary += '\nTop 10 document types currently in database:\n'
        contents = self.database.list_doctypes().items()
        for k,v in sorted(self.database.list_doctypes().items(), key=lambda x: x[1], reverse=True)[:10]:
            summary += "{k:30} : {v:10}\n".format(**locals())
        if len(contents)>10:
            summary += "...\n"
        return summary

### COMMANDLINE SPECIFICATION ###

def commandline():

    usage  = "Usage: %prog [options] tasktype task\ne.g. : %prog scrapers diewelt"

    parser = OptionParser(usage=usage)

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                    help='Whether to print progress')
    parser.add_option('-d', '--debug', dest='debug', default=False, action='store_true',
                    help='Print all debugging info')
    parser.add_option('-s', '--silent', dest='silent', default=False, action='store_true',
                    help='Refrain from returning documents to stdout (for unix piping) ')
    parser.add_option('-c','--celery', dest='celery', default=False, action='store_true',
                    help='Put tasks in the celery cluster instead of running them locally')

    options, args = parser.parse_args()

    if len(args)==0:
        print(__doc__)
        parser.print_help()
        return

    inca = Inca()
    if not len(args)>=2:
        print(inca._summary())
        return

    tasktype = args[0]
    task     = args[1]

    try:
        tasktype_ob = getattr(inca,tasktype)
    except:
        print("Tasktype '{tasktype}' not found! Should be 'scrapers' or 'processing'".format(**locals()))
        return
    try:
        task_func   = getattr(tasktype_ob, task)
    except:
        tasklist    = ',\n'.join([t for t in dir(tasktype_ob) if '__' not in t])
        print("Unknown task '{task}' not found, for {tasktype} this should be in:\n{tasklist}".format(**locals()))
        return

    if options.verbose:
        logger.setLevel('INFO')

    if options.celery:
        action = 'celery_batch'
    else:
        action = 'run'

    logger.info("running {tasktype} : {task}".format(**locals()))
    task_func(action=action, *args[2:])
    logger.info("finished {tasktype} : {task}".format(**locals()))


if __name__ == '__main__':
    commandline()
