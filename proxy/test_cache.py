from nose.tools import eq_, ok_
import os
import shutil
from proxy.cache import LRUCache


def setup_module():
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')

def teardown_module():
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')

def test_cache_defaults():
    cache = LRUCache(cache_dir='tmp')
    cache['test'] = 'blah'
    ok_('test' in cache)
    ok_('blah' not in cache)

def test_cache_eviction():
    cache = LRUCache(cache_dir='tmp', capacity=5)
    cache['test1'] = 'blah'
    ok_('test1' in cache)
    cache['test2'] = 'blah'
    ok_('test1' in cache)
    ok_('test2' in cache)
    cache['test3'] = 'blah'
    ok_('test1' not in cache)
    ok_('test2' in cache)
    ok_('test3' in cache)
