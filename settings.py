import os

class Production():
    MONGO_HOST     = os.environ.get('MONGO_HOST','localhost')
    MONGO_PORT     = os.environ.get('MONGO_PORT', 27017)
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE','inca')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME','')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD','')
    FLASK_DEBUG    = False
    LOGLEVEL       = 'WARNING'

class Debug(Production):
    FLASK_DEBUG = True
    LOGLEVEL = 'DEBUG'
    
class Testing(Debug):
    MONGO_DATABASE = 'testing'
