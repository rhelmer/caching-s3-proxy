"""
Filesystem-backed LRU cache. Not threadsafe.
"""

import collections
import os
import cPickle as pickle
import tempfile


class LRUCache(object):
    def __init__(self, capacity=1000, cache_dir=tempfile.gettempdir()):
        self.capacity = capacity
        self.cache = collections.OrderedDict()
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        self.index_file = os.path.join(self.cache_dir, 'index')
        if os.path.exists(self.index_file):
            self.cache = pickle.load(open(self.index_file, 'r'))

    def __getitem__(self, key):
        self.cache.pop(key)
        self.cache[key] = 1
        with open(os.path.join(self.cache_dir, key), 'r') as cachefile:
            return cachefile.read()

    def __setitem__(self, key, value):
        if len(self.cache) >= self.capacity:
            cache_key, file_path = self.cache.popitem(last=False)
            os.remove(os.path.join(self.cache_dir, cache_key))
        self.cache[key] = 1
        with open(os.path.join(self.cache_dir, key), 'w') as cachefile:
            cachefile.write(value)
        pickle.dump(self.cache, open(self.index_file, 'w'))

    def __contains__(self, key):
        return key in self.cache
