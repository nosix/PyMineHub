"""
>>> get_value(ConfigKey.BATCH_COMPRESS_THRESHOLD)
256
>>> set_config(batch_compress_threshold=128)
>>> get_value(ConfigKey.BATCH_COMPRESS_THRESHOLD)
128
>>> reset()
>>> get_value(ConfigKey.BATCH_COMPRESS_THRESHOLD)
256
"""
from enum import Enum


class ConfigKey(Enum):
    BATCH_COMPRESS_THRESHOLD = 1
    SEED = 2
    WORLD_NAME = 3


__default_config = (
    (ConfigKey.BATCH_COMPRESS_THRESHOLD, 256),
    (ConfigKey.SEED, 0),
    (ConfigKey.WORLD_NAME, 'PyMineHub Server')
)

_config = dict(__default_config)


def reset():
    _config.clear()
    _config.update(__default_config)


def set_config(**kwargs):
    _config.update(dict((ConfigKey[key.upper()], value) for key, value in kwargs.items()))


def get_value(key: ConfigKey):
    return _config[key]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
