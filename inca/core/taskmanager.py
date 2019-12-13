"""
The taskmanager provides task-scheduling and execution functionality. 

CURRENT IMPLEMENTATION IN JSON dump !
"""

import json
from datetime import timedelta
import configparser
import celery
import os
import logging

logger = logging.getLogger("INCA")

config = configparser.ConfigParser()
config.read("settings.cfg")

taskfile = config.get("celery", "taskfile")

TASK_INTERVALS = ["1sec", "30sec", "1min", "30min", "1hour", "24hour", "week"]


def verify_task(task):
    type_correct = type(task) == dict
    has_task = "task" in task.keys()
    schedule_is_time = task.get("schedule") in TASK_INTERVALS
    has_args_key = "args" in task.keys()
    has_kwargs_key = "kwargs" in task.keys()
    all_checks_out = type_correct and has_task and schedule_is_time
    assert (
        all_checks_out
    ), "type correct: {type_correct}, has_task: {has_task}, schedule_is_time: {schedule_is_time}".format(
        **locals()
    )

    return all_checks_out


def get_tasks(interval="all"):
    if taskfile in os.listdir("."):
        try:
            tasks = json.load(open(taskfile))
            return {
                taskname: task
                for taskname, task in tasks.items()
                if interval == "all" or task.get("schedule", "") == interval
            }
        except Exception as e:
            logger.warn("could not import tasks, empty file? {e}".format(**locals()))
            return {}
    else:
        return {}


def add_task(task):
    """
    Schedules tasks for recurrent execution

    Parameters
    ----------
    task: dict
        a task to be scheduled. Should be configured as follows:
            name : string naming this job
            schedule: string, from {TASK_INTERVALS}
            function : required function, e.g. 'scrapers'
            task    : required task, e.g. 'proceedings_NL'
            args    : tuple of optional positional arguments
            kwargs  : dict of optional keyword arguments

    Returns
    -------

    """
    if not "args" in task.keys():
        task["args"] = ()
    if not "kwargs" in task.keys():
        task["kwargs"] = dict()
    if verify_task(task):
        tasks = get_tasks()
        if task["name"] in tasks.keys():
            return "task already exists"
        tasks.update({task["name"]: task})
        json.dump(tasks, open(taskfile, "w"))
    else:
        return "task not scheduled"
    return "task scheduled"


def remove_task(taskname):
    tasks = get_tasks()
    if taskname in tasks.keys():
        tasks.pop(taskname)
        json.dump(tasks, open(taskfile, "w"))
    else:
        return "task [{taskname}]not found".format(**locals())
    return "task [{taskname}] removed from schedule".format(**locals())


############
#
# Elasticsearch mapping
#
############

task_mapping = {
    "mappings": {
        "task": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "description": {"type": "string"},
            "schedule": {"type": "string"},
            "function": {"type": "string"},
            "task": {"type": "string"},
            "owner": {"type": "string"},
            "added_date": {"type": "strict_date_optional_time||epoch_millis"},
            "last_update": {"type": "strict_date_optional_time||epoch_millis"},
            "args": {"type": "object"},
            "kwargs": {"type": "object"},
        }
    }
}
