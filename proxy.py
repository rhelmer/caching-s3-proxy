#!/usr/bin/env python
"""
Caching S3 Proxy - provides an unauthenticated plain HTTP frontend 
    for public and private S3 buckets, and caches on the filesystem.
    Least Recently Used objects are evicted from the cache first.

example:
    python proxy.py &
    curl localhost:8000/org.mozilla.crash-stats.symbols-private/v1/symupload-1.0-Linux-20120709194529-symbols.txt
"""

import boto
from boto.s3.key import Key
import collections
import hashlib
import os
import cPickle as pickle
from wsgiref.simple_server import make_server

PORT=8000

class LRUCache:
    def __init__(self, capacity, cache_dir):
        self.capacity = capacity
        self.cache = collections.OrderedDict()
        self.cache_dir = cache_dir
        self.index_file = os.path.join(self.cache_dir, 'index')
        if os.path.exists(self.index_file):
            self.cache = pickle.load(open(self.index_file, 'r'))

    def __getitem__(self, key):
        try:
            self.cache.pop(key)
            self.cache[key] = 1
            with open(os.path.join(self.cache_dir, key), 'r') as cachefile:
                return cachefile.read()
        except KeyError:
            return -1

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

cache = LRUCache(capacity=10, cache_dir='/tmp/cache')

def proxy_s3_bucket(environ, start_response):
    """proxy private s3 buckets"""
    path_info = environ.get('PATH_INFO', '')
    path_info = path_info.lstrip('/')
    (bucket, key) = path_info.split('/', 1)
    s3_result = fetch_s3_object(bucket, key)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [s3_result]

def fetch_s3_object(bucket, key):
    m = hashlib.md5()
    m.update(bucket+key)
    cache_key = m.hexdigest()

    conn = boto.connect_s3()
    if cache_key in cache:
        return cache[cache_key]

    b = conn.get_bucket(bucket)
    k = b.get_key(key)
    obj = k.get_contents_as_string()
    cache[cache_key] = obj
    return obj

if __name__ == '__main__':
    httpd = make_server('', PORT, proxy_s3_bucket)
    print 'Serving HTTP on port %s...' % PORT
    httpd.serve_forever()
