"""
Filesystem-backed LRU cache.
"""

import ordereddict
from contextlib import contextmanager
import cPickle as pickle
import logging
import os
import tempfile
import time


class LRUCache(object):
    def __init__(self, capacity=None, cache_dir=None):
        if not capacity:
            # 1GB
            capacity = (10*10**9)
        if not cache_dir:
            cache_dir = tempfile.gettempdir()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.capacity = capacity
        self.cache = ordereddict.OrderedDict()
        self.cache_dir = cache_dir
        self.total_size = 0
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        self.lock_path = os.path.join(self.cache_dir, 'lock')
        self.logger.info('using cache dir %s' % self.cache_dir)
        self.index_file = os.path.join(self.cache_dir, 'index')
        with flock(self.lock_path):
            if os.path.exists(self.index_file):
                (self.total_size, self.cache) = \
                        pickle.load(open(self.index_file, 'r'))
            else:
                pickle.dump((self.total_size, self.cache),
                            open(self.index_file, 'w'))

    def __getitem__(self, key):
        abspath = os.path.join(self.cache_dir, key)
        with flock(self.lock_path):
            (self.total_size, self.cache) = \
                    pickle.load(open(self.index_file, 'r'))
            self.cache.pop(key)
            size = os.path.getsize(abspath)
            with open(abspath, 'r') as cachefile:
                value = cachefile.read()
                # bump this to the top, since it was accessed most recently
                self.cache[key] = size
                pickle.dump((self.total_size, self.cache),
                        open(self.index_file, 'w'))
                return value

    def __setitem__(self, key, value):
        abspath = os.path.join(self.cache_dir, key)
        with flock(self.lock_path):
            if os.path.exists(self.index_file):
                (self.total_size, self.cache) = \
                        pickle.load(open(self.index_file, 'r'))
            # remove files until we're under the limit, if we hit capacity
            while self.total_size >= self.capacity:
                self.logger.info('cache hit capacity %s' % self.capacity)
                cache_key, size = self.cache.popitem(last=False)
                os.remove(os.path.join(self.cache_dir, cache_key))
                self.logger.info('evicted %s from cache' % cache_key)
                self.total_size -= size
            with open(abspath, 'w') as cachefile:
                cachefile.write(value)
            size = os.path.getsize(abspath)
            self.cache[key] = size
            self.total_size += size
            pickle.dump((self.total_size, self.cache),
                    open(self.index_file, 'w'))

    def __contains__(self, key):
        return key in self.cache


# based on https://github.com/erikrose/shiva
# and also https://github.com/dmfrey/FileLock
@contextmanager
def flock(lock_path, timeout=300):
    """Context manager that acquires and releases a file-based lock.
    """
    start_time = time.time()
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT|os.O_EXCL)
            break
        except OSError:
            if (time.time() - start_time) >= timeout:
                raise Exception("Timeout occured.")

    try:
        yield fd
    finally:
        if fd:
            os.close(fd)
            os.remove(lock_path)
