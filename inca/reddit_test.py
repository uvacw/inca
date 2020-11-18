# Initialize INCA
import os
os.getcwd()
os.chdir('./inca')
from inca import Inca
myinca = Inca() # get an instance of INCA
myinca.database.list_apps() # see which apps already exist

# one time: create a reddit app and add credentials
# myinca.clients.reddit_remove_app('health_convos')
myinca.clients.reddit_create_app() # create a Reddit app

myinca.clients.reddit_create_credentials(appname='health_convos')
myinca.clients.reddit_posts(app='health_convos', subreddit_name='Netherlands')
myinca.database.delete_doctype('reddit_post')
myinca.database.doctype_first('reddit_post')

from pprint import pprint
for doc in myinca.database.document_generator('doctype:"reddit_post"'):
    pprint(doc)

from pathlib import Path
myinca.importers_exporters.export_json_file(query = 'doctype:"reddit_post"',
                                            destination = os.path.join(Path(os.getcwd()).parents[1],'health_convos','inca_export','inca_reddit.json'))


# Notes for Wednesday (Aug 26):
# 1) reddit_client as-is: note that Reddit API (so PRAW too) has limit of 1,000 results
    # https://pushshift.io/ might be an option if dataset needs to be more comprehensive (don't know how it works atm)
    # remove all ES indices
    # example Submission
    # example 5 recent Submissions
    # Q: default app vs. credentialed app; clarify how adding credentials should differ
        # for reddit, the app is created within a specific user account and
        # the username/password aren't required for the read-only version we need


# 2) ES mapping error: run Reddit client code on ES 6.x database which hasn't had YouTube or Twitter clients before.
    # a) elasticsearch.exceptions.RequestError: RequestError(400, 'illegal_argument_exception', 'Rejecting mapping update to [.apps] as the final mapping would have more than 1 type: [youtube, reddit]')
    # b) deleting existing youtube app wasn't sufficient, still got error. Deleted ES indices to start fresh.
        # curl -X DELETE "localhost:9200/inca?pretty"
        # curl -X DELETE "localhost:9200/.credentials?pretty"
        # curl -X DELETE "localhost:9200/.apps?pretty"
    # c) INCA doesn't work with ES 7.x (error with 'schema.json'). ES 6.x works, but only 1 type allowed.
        # https://www.elastic.co/guide/en/elasticsearch/reference/7.x/removal-of-types.html
        # "Indices created in Elasticsearch 7.0.0 or later no longer accept a _default_ mapping.
        # Indices created in 6.x will continue to function as before in Elasticsearch 6.x.
        # Types are deprecated in APIs in 7.0, with breaking changes to the index creation,
        # put mapping, get mapping, put template, get template and get field mappings APIs."


# 2) __main__.py: not sure how this works, but I think Celery inserted a new function "reddit_create_credentials"
    # a) should this file be excluded when committing to Git?


# 3) Updated "Requirements.txt" and "setup.py" to nl-core-news-sm==2.3.0
    # a) SpaCy-related error at "nl-core-news-sm==2.3.0”
        # sudo pip3 install -r Requirements
            # https://github.com/uvacw/inca/blob/development/doc/gettingstarted.md
        # SpaCy developer says that it’s not available as a standalone package
            # https://stackoverflow.com/questions/50853997/unable-to-install-spacy-english-model-in-python-3-5
        # SpaCy documentation (https://spacy.io/usage/models#models-download) suggests this format:
            # spacy>=2.2.0,<3.0.0
            # https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz#egg=en_core_web_sm
    # b) some conflicts between INCA and SpaCy b/c Requirements.txt file needs versions of packages which SpaCy wants more recent versions of.


# 4) client_class.py: commented out some logging in the store_credentials function
    # guessing earlier ES (pre 6.x?) return a "created" key; not available now


# 5) auto-start ES on boot-up
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/starting-elasticsearch.html
    # sudo /bin/systemctl daemon-reload
    # sudo /bin/systemctl enable elasticsearch.service


# TODO: hashing IDs and username info (within submission and comment functions)
# TODO: reddit_client - remove 'username' from add_application; instead, prompt in add_credentials to get 'username'
# TODO: current code results in error when credentials aren't available
    # am I supposed to add 'default' credentials so that the 'default' app works?
# TODO: client_class.py - find another field for logging info?
# TODO: 'tree' of example Submission
# TODO: add tag processor #524

