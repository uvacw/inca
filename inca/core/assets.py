'''
This file provides the assets management.

assets are lists of dicts, usually understood as imported tables
'''

from .database import client
import logging
import datetime
from .basic_utils import dotkeys

logger = logging.getLogger(__name__)

def put_asset( user, name, project, LOD):
    asset = {
        'user':[user],
        'name':name,
        'project':project,
        'added_at' : datetime.datetime.now(),
        'content':LOD
    }
    client.index('assets', doc_type=project, body=asset)
    logger.info("added {name} to asset store".format(**locals()))
    return True

def get_asset(id=None, name=None):
    if not id and not name:
        info.warning("requires either id or name! None given...")
        return False
    if id:
        return client.get('assets', id=id)
    elif name:
        units = client.search('assets', body={'filter':{'match':{'name':name}}})['hits']['hits']
    if len(units)==1:
        return units[0]
    elif len(units)<1:
        logger.warning("ambiguous designation! Use ID?")
        return {}
    else:
        logger.info("no asset found matching this {name}[{id}]".format(**locals()))
        return {}

def delete_asset(id):
    client.delete('assets',id=id)
    logger.info("deleted {id} from asset store".format(**locals()))
    pass


def update_asset(id=None, name=None):
    # TODO: THIS SHOULD TOTALLY BE IMPLEMENTED!
    pass

def list_assets():
    return [{'id':asset.get('_id'),
             'name': dotkeys(asset,'_source.name'),
             'project':dotkeys(asset, '_source.project'),
             'added':dotkeys(asset,'_source.added_at'),
             'length':len(dotkeys(asset,'_source.content'))} for
            asset in client.search('assets')['hits']['hits']]

def from_csv():
    pass
