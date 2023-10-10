"""
Redis connection pool and connection object. Use redis_conn as the connection object.
"""
import os
import redis

# FIXME This should be singleton at least, or IOC

pool = redis.ConnectionPool(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'),
                            db=0, decode_responses=True)
redis_conn = redis.Redis(connection_pool=pool)
