import redis

from env_config import env


class Redis:
    """ Use this singleton to interact with the Redis instance. DO NOT CREATE OTHER CONNECTIONS """
    _conn = None

    def __new__(cls):
        return cls

    @classmethod
    def conn(cls):
        """ Return a connection to Redis server ready to be used like this: Redis.conn().lpush(*args) """
        if cls._conn is None:
            cls._conn = redis.StrictRedis(host=env.REDIS_HOST, port=env.REDIS_PORT, db=env.REDIS_DB)
        return cls._conn
