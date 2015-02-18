#!/usr/bin/env python
"""
Caching S3 Proxy - provides an unauthenticated plain HTTP frontend 
    for public and private S3 buckets, and caches on the filesystem.
    Least Recently Used objects are evicted from the cache first.

example:
    python proxy.py &
    curl localhost:8000/org.mozilla.crash-stats.symbols-private/v1/symupload-1.0-Linux-20120709194529-symbols.txt
"""

import proxy
from wsgiref.simple_server import make_server

PORT=8000

if __name__ == '__main__':
    httpd = make_server('', PORT, proxy.proxy_s3_bucket)
    print 'Serving HTTP on port %s...' % PORT
    httpd.serve_forever()
