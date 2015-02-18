"""
Filesystem-backed LRU cache. Not threadsafe.
"""

import collections
import os
import cPickle as pickle
import logging
import tempfile


class LRUCache(object):
    def __init__(self, capacity=(10*10**9), cache_dir=tempfile.gettempdir()):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.capacity = capacity
        self.cache = collections.OrderedDict()
        self.cache_dir = cache_dir
        self.total_size = 0
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        self.logger.info('using cache dir %s' % self.cache_dir)
        self.index_file = os.path.join(self.cache_dir, 'index')
        if os.path.exists(self.index_file):
            self.cache = pickle.load(open(self.index_file, 'r'))

    def __getitem__(self, key):
        self.cache.pop(key)
        abspath = os.path.join(self.cache_dir, key)
        size = os.path.getsize(abspath)
        with open(abspath, 'r') as cachefile:
            value = cachefile.read()
            # bump this to the top, since it was accessed most recently
            self.cache[key] = size
            return value

    def __setitem__(self, key, value):
        # remove files until we're under the limit, if we hit capacity
        while self.total_size >= self.capacity:
            self.logger.info('cache hit capacity %s' % self.capacity)
            cache_key, size = self.cache.popitem(last=False)
            os.remove(os.path.join(self.cache_dir, cache_key))
            self.logger.info('evicted %s from cache' % cache_key)
            self.total_size -= size
        abspath = os.path.join(self.cache_dir, key)
        with open(abspath, 'w') as cachefile:
            cachefile.write(value)
        size = os.path.getsize(abspath)
        self.cache[key] = size
        self.total_size += size
        pickle.dump(self.cache, open(self.index_file, 'w'))

    def __contains__(self, key):
        return key in self.cache
