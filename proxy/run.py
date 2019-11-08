#!/usr/bin/env python
import os
from proxy import CachingS3Proxy
import tempfile
from wsgiref.simple_server import make_server


def main():
    capacity = int(os.environ.get('CAPACITY', 1000000000))
    cache_dir = os.environ.get('CACHEDIR', tempfile.gettempdir())
    p = CachingS3Proxy(capacity, cache_dir)
    port = int(os.environ.get('PORT', 8000))
    httpd = make_server('', port, p.proxy_s3_bucket)
    print('Serving HTTP on port %s...' % port)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
