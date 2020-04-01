Caching S3 Proxy
================

Provides an unauthenticated plain HTTP frontend
for public and private S3 buckets, and caches on the filesystem.
Least Recently Used objects are evicted from the cache first.

Running Standalone
------------------

Example:
```
  python setup.py install
  export AWS_ACCESS_KEY_ID=...
  export AWS_SECRET_ACCESS_KEY=...
  caching-s3-proxy &
  curl localhost:8000/my_bucket/v1/my_file.txt
```

If you want to listen on a different port, just set the `PORT` variable:
```
  PORT=9999 caching-s3-proxy
```

The capacity of the cache is limited to 1GB by default, and the proxy will attempt to remove cached objects to stay under this limit. If you expect to go over this limit, you can set the `CAPACITY` variable (in bytes):

```
  CAPACITY=2000000000 caching-s3-proxy
```

Cached object files are stored by default wherever your OS leaves temporary files, but this can be modified by setting the `CACHEDIR` variable:

```
  CACHEDIR=/mnt/tmp caching-s3-proxy
```

uWSGI
-----

Alternatively, you can run under uwsgi. It's safe to use multiple worker
processes (the shared file cache uses file locking to allow concurrency):
```
  uwsgi -w proxy.wsgi --http=localhost:8000 --workers=10
```

If you want to put this behind Nginx or Apache, use a socket instead:
```
  uwsgi -w proxy.wsgi -s /var/run/caching-s3-proxy.sock --workers=10
```

Then see http://uwsgi-docs.readthedocs.org/en/latest/Nginx.html or
http://uwsgi-docs.readthedocs.org/en/latest/Apache.html
