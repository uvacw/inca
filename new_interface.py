'''

'''

import os
import logging

logger = logging.getLogger(__name__)


if not 'settings.cfg' in os.listdir('.'):
    logger.info('No settings found, applying default settings (change in `settings.cfg`)')
    from shutil import copyfile
    copyfile('default_settings.cfg','settings.cfg')

from celery import Celery, group, chain, chord
from flask import Flask
import argparse
import core
import configparser
import core.search_utils
import core.taskmanager
import datetime
import processing # helps celery recognize the processing tasks
import scrapers   # helps celery recognize the scraping tasks
import clients    # helps celery recognize client tasks
import analysis   # helps celery recognize analysis tasks


from core.database import config


class Inca():

    _taskmaster = Celery(
        backend = config.get('celery', '%s.backend' %config.get('inca','dependencies')),
        broker  = config.get('celery', '%s.broker' %config.get('inca','dependencies')),
    )

    database = core.search_utils

    def __init__(self):
        self._construct_tasks('scrapers')
        self._construct_tasks('processing')

    class scrapers():
        '''Scrapers for various (news) outlets '''
        pass

    class processing():
        '''Processing options to operate on documents'''
        pass
        
    def _construct_tasks(self, function):
        for k,v in self._taskmaster.tasks.items():
            functiontype = k.split('.',1)[0]
            taskname     = k.rsplit('.',1)[1]
            if functiontype == function:
                setattr(getattr(self,function),taskname,self._taskmaster.tasks[k])
                
