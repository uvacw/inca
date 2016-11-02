from datetime import timedelta


def get_scheduler():
    return {
        "1sec_scheduler": {
            "task": "inca.run_scheduled",
            "kwargs": {"interval": "1sec"},
            "schedule": timedelta(seconds=1)
        },
        "30sec_scheduler": {
            "task": "inca.run_scheduled",
            "kwargs": {"interval": "30sec"},
            "schedule": timedelta(seconds=30)
        },
        "1min_scheduler": {
            "task": "inca.run_scheduled",
            "kwargs": {"interval": "1min"},
            "schedule": timedelta(minutes=1)
        },
        "30min_scheduler": {
            "task": "inca.run_scheduled",
            "kwargs": {"interval": "30min"},
            "schedule": timedelta(minutes=30)
        },
        "1hour_scheduler": {
            "task": "inca.run_scheduled",
            "kwargs": {"interval": "1hour"},
            "schedule": timedelta(hours=1)
        },
        "1day_scheduler": {
            "task": "inca.run_scheduled",
            "kwargs": {"interval": "1day"},
            "schedule": timedelta(days=1)
        },
    }
