
from configparser import ConfigParser
from redis import from_url


def get_redis_conn(config_uri):
    """

    :param config_uri:
    :return:
    """
    parser = ConfigParser()
    parser.read(config_uri)
    redis_url = parser.get('app:main', 'redis.url')
    return from_url(redis_url)


def get_redis_number(connection, key):
    res_str = connection.get(key)
    if res_str is not None and res_str != b'None':
        return float(res_str)
    return None
