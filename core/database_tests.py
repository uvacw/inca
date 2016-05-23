import nose
from database import *

def setup_func():
    index = 'testing'
    testdoc = {'title':'hello world', 'body':'the body of the document'}
    indexed_document = client.index(index, 'doc-nl',testdoc)
    global indexed document

def teardown_func():
    client.indices.delete('testing')

@with_setup(setup_func, teardown_func)
def test_check_exists():
    assert check_exists('random_id')[0]==False
    assert check_exists(indexed_document['_id'])[0]==True
    pass

@with_setup(setup_func, teardown_func)
def test_update_document():
    pass

@with_setup(setup_func, teardown_func)
def test_delete_document():
    pass

@with_setup(setup_func, teardown_func)
def test_insert_document():
    pass

@with_setup(setup_func, teardown_func)
def test_update_or_insert_document():
    pass
