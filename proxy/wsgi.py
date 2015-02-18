import os
import tempfile
from proxy import CachingS3Proxy

def application(environ, start_response):
    capacity = int(os.environ.get('CAPACITY', 1000000000))
    cache_dir = os.environ.get('CACHEDIR', tempfile.gettempdir())
    p = CachingS3Proxy(capacity, cache_dir)
    return p.proxy_s3_bucket(environ, start_response)
