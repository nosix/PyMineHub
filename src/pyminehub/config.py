"""
>>> get_value(ConfigKey.batch_compress_threshold)
256
>>> set_config(batch_compress_threshold=128)
>>> get_value(ConfigKey.batch_compress_threshold)
128
>>> reset()
>>> get_value(ConfigKey.batch_compress_threshold)
256
"""
from enum import Enum


class ConfigKey(Enum):
    batch_compress_threshold = 1


__default_config = (
    (ConfigKey.batch_compress_threshold, 256),
)

_config = dict(__default_config)


def reset():
    _config.clear()
    _config.update(__default_config)


def set_config(**kwargs):
    _config.update(dict((ConfigKey[key], value) for key, value in kwargs.items()))


def get_value(key: ConfigKey):
    return _config[key]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
