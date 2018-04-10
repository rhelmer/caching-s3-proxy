import boto3
import botocore
import hashlib
import logging
from proxy.cache import LRUCache
import tempfile


class CachingS3Proxy(object):
    def __init__(self, capacity=(10*10**9), cache_dir=tempfile.gettempdir()):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.cache = LRUCache(capacity, cache_dir)
        self.s3 = boto3.resource('s3')

    def proxy_s3_bucket(self, environ, start_response):
        """proxy private s3 buckets"""
        path_info = environ.get('PATH_INFO', '')
        if path_info == '/':
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return ['Caching S3 Proxy']

        path_info = path_info.lstrip('/')
        (bucket, key) = path_info.split('/', 1)
        try:
            s3_result = self.fetch_s3_object(bucket, key)
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
        except botocore.exceptions.ClientError as ce:
            s3_result = ce.response['Error']['Message']
            status = '404 NOT FOUND'
            response_headers = [('Content-type', 'text/plain')]

        start_response(status, response_headers)
        return [s3_result]

    def fetch_s3_object(self, bucket, key):
        m = hashlib.md5()
        m.update(bucket+key)
        cache_key = m.hexdigest()

        try:
            return self.cache[cache_key]
        except KeyError:
            self.logger.debug('cache miss for %s' % cache_key)

            obj = self.s3.Object(bucket, key).get()
            body = obj['Body'].read()
            self.cache[cache_key] = body
            return body
