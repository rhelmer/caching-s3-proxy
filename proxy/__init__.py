import boto
from boto.s3.key import Key
import hashlib
import logging
from proxy.cache import LRUCache
import tempfile


class CachingS3Proxy(object):
    def __init__(self, capacity=(10*10**9), cache_dir=tempfile.gettempdir()):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.cache = LRUCache(capacity, cache_dir)

    def proxy_s3_bucket(self, environ, start_response):
        """proxy private s3 buckets"""
        path_info = environ.get('PATH_INFO', '')
        path_info = path_info.lstrip('/')
        (bucket, key) = path_info.split('/', 1)
        s3_result = self.fetch_s3_object(bucket, key)
        if s3_result:
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [s3_result]
        else:
            status = '404 NOT FOUND'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return []

    def fetch_s3_object(self, bucket, key):
        m = hashlib.md5()
        m.update(bucket+key)
        cache_key = m.hexdigest()

        conn = boto.connect_s3()
        if cache_key in self.cache:
            self.logger.debug('cache hit for %s' % cache_key)
            return self.cache[cache_key]
        else:
            self.logger.debug('cache miss for %s' % cache_key)

        b = conn.get_bucket(bucket)
        k = b.get_key(key)
        if k:
            obj = k.get_contents_as_string()
            self.cache[cache_key] = obj
            return obj
        else:
            return None
