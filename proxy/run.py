#!/usr/bin/env python
from proxy import CachingS3Proxy
from wsgiref.simple_server import make_server

PORT=8000

def main():
    p = CachingS3Proxy()
    httpd = make_server('', PORT, p.proxy_s3_bucket)
    print 'Serving HTTP on port %s...' % PORT
    httpd.serve_forever()

if __name__ == '__main__':
    main()
