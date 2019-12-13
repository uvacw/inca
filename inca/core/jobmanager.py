"""
"""


class jobmanager:
    def __init__(self, client):
        """
        starts a new jobmanager instance
        
        input
        ---
        client : ElasticSearch()
            Client object for database access
        """
        self.client = client

    def add_job(
        self,
        function,
        task,
        timing,
        input_documents=None,
        as_batch=False,
        *args,
        **kwargs
    ):
        """
        Adds jobs to the the job scheduler
        
        input
        ---
        function: string
            INCA function type (scraper, processor etc)
        task: string
            INCA task available under function
        timing: string
            string specifying every hour (hourly), every day (daily) etc
        as_batch: Boolean
            True/False value expressing whether the task should call 'batch_do'
            instead of 'do'
        input_documents: string, list or dict
            Specification of documents to run the job on. Can be empty (for scrapers) or contain
            either a string (denoting the doctype), list (with documents) or dict (elasticsearch query)
        """
        # TODO

    def list_jobs(self):
        """Lists all jobs currently pending"""
        # TODO

    def remove_job(self, job_id):
        """removes a job from the scheduler
        
        input
        ---
        job_id: string
            job_id to remove from database
        """
        # TODO

    def run_jobs(self):
        """Run jobs in scheduler"""
        # TODO
