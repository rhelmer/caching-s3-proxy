Caching S3 Proxy 
----

Provides an unauthenticated plain HTTP frontend 
for public and private S3 buckets, and caches on the filesystem.
Least Recently Used objects are evicted from the cache first.

Example:
```
  python setup.py install
  cachings3proxy &
  curl localhost:8000/org.mozilla.crash-stats.symbols-private \
    /v1/symupload-1.0-Linux-20120709194529-symbols.txt
```
