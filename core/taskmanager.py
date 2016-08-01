'''
The taskmanager provides task-scheduling and execution functionality. 

'''

import json
from inca import taskmaster
from time import timedelta
import configparser

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))

taskfile = config.get('celery','taskfile')

def verify_task(task):
    type_correct     = type(task)==dict
    has_task         = 'task' in task.keys()
    task_exists      = 'task' in taskmaster.tasks.keys()
    schedule_is_time = type(task.get('schedule',{}))==timedelta
    all_checks_out = type_correct and has_task and task_exists and schedule_is_time
    return all_checks_out

def get_tasks():
    tasks = json.load(open(taskfile))
    return tasks

def add_task(task):
    if verify_task(task):
        tasks = get_tasks()
        if task in tasks.keys():
            return "task already exists"
        tasks.update(task)
        json.dump(tasks, open(taskfile, 'w'))
    return "task scheduled"

def remove_task(taskname):
    tasks = get_tasks()
    if taskname in tasks.keys():
        tasks.pop(taskname)
        json.dump(tasks, open(taskfile,'w'))
    else:
        return "task not found"
    return "task scheduled"

