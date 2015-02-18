#!/usr/bin/env python

import proxy
from wsgiref.simple_server import make_server

PORT=8000

if __name__ == '__main__':
    httpd = make_server('', PORT, proxy.proxy_s3_bucket)
    print 'Serving HTTP on port %s...' % PORT
    httpd.serve_forever()
