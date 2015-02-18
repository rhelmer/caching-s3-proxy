from proxy import CachingS3Proxy

def application(environ, start_response):
    p = CachingS3Proxy()
    return p.proxy_s3_bucket(environ, start_response)
