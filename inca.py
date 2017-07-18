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
from interface import make_interface


class Inca():

    _taskmaster = Celery(
        backend = config.get('celery', '%s.backend' %config.get('inca','dependencies')),
        broker  = config.get('celery', '%s.broker' %config.get('inca','dependencies')),
    )

    database = core.search_utils

    _prompt = "Placeholder"

    def __init__(self, prompt="TLI", distributed=False, verbose=True):
        self._LOCAL_ONLY = distributed
        self._prompt = getattr(make_interface,prompt).prompt
        self._construct_tasks('scrapers')
        self._construct_tasks('processing')
        self._construct_tasks('clients')
        if verbose:
            logger.setLevel('INFO')

    class scrapers():
        '''Scrapers for various (news) outlets '''
        pass

    class processing():
        '''Processing options to operate on documents'''
        pass

    class clients():
        '''Clients to access (social media) APIs'''
        pass

    def _construct_tasks(self, function):
        for k,v in self._taskmaster.tasks.items():
            functiontype = k.split('.',1)[0]
            taskname     = k.rsplit('.',1)[1]
            if functiontype == function:
                target_task = self._taskmaster.tasks[k]
                target_task.prompt = self._prompt

                is_client_main_class = hasattr(target_task,"service_name") and target_task.__name__== target_task.service_name
                if is_client_main_class:
                    setattr(getattr(self,function),
                        "{service_name}_create_app".format(service_name=target_task.service_name), target_task.add_application )
                    setattr(getattr(self,function),
                        "{service_name}_remove_app".format(service_name=target_task.service_name), target_task.remove_application )
                    setattr(getattr(self,function),
                        "{service_name}_create_credentials".format(service_name=target_task.service_name), target_task.add_credentials )
                else:
                    setattr(getattr(self,function),taskname,target_task.runwrap)

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
    parser.add_option('-np', '--no-prompt', dest='noprompt',default=False, action='store_true',
                    help='Never prompt users (usually leads to failure), usefull for headles environments and cronjobs')

    options, args = parser.parse_args()

    if len(args)==0:
        print(__doc__)
        parser.print_help()
        return

    if options.noprompt:
        prompt="noprompt"
    else:
        prompt="TLI"

    inca = Inca(prompt=prompt)
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
        logging.basicConfig(level='INFO')

    if options.debug:
        logging.basicConfig(level='DEBUG')

    if options.celery:
        action = 'celery_batch'
    else:
        action = 'run'

    logger.info("running {tasktype} : {task}".format(**locals()))
    task_func(action=action, *args[2:])
    logger.info("finished {tasktype} : {task}".format(**locals()))

if __name__ == '__main__':
    commandline()
