
from configparser import ConfigParser
from redis import Redis

def get_redis_conn(config_uri):
    parser = ConfigParser()
    parser.read(config_uri)
    redis_data = parser.get('app:main', 'redis.url').split(':')
    redis_data.pop(0)
    host = redis_data[0].replace('//', '')
    port = int(redis_data[1])
    return Redis(host, port)
