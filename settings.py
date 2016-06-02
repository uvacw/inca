import os
import settings

class Production():
    ELASTIC_HOST   = os.environ.get('ELASTIC_HOST','0.0.0.0')
    ELASTIC_PORT   = os.environ.get('ELASTIC_PORT', 9200)
    ELASTIC_DATABASE = os.environ.get('ELASTIC_DATABASE','inca')

    # NOT IMPLEMENTED as of now
    ELASTIC_USERNAME = os.environ.get('ELASTIC_USERNAME','')
    ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD','')


    FLASK_DEBUG    = False
    # /not implemented

    LOGLEVEL       = 'WARNING'

class Debug(Production):
    FLASK_DEBUG = True
    LOGLEVEL = 'DEBUG'
    
class Testing(Debug):
    ELASTIC_DATABASE = 'testing'

def get_config(level):
    return getattr(settings, level)
