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
from random import randrange
from typing import Dict, Any

from pyminehub.typevar import T


class ConfigKey(Enum):
    # system
    IP_VERSION = 101
    SERVER_PORT = 102
    MAX_LOG_LENGTH = 103
    # raknet
    SERVER_GUID = 201
    RESEND_TIME = 202
    # mcpe.world
    SEED = 301
    DIFFICULTY = 302
    RAIN_LEVEL = 303
    LIGHTNING_LEVEL = 304
    # raknet and mcpe.world
    WORLD_NAME = 401
    GAME_MODE = 402
    # mcpe.network
    BATCH_COMPRESS_THRESHOLD = 501


__default_config = (
    (ConfigKey.IP_VERSION, 4),
    (ConfigKey.SERVER_PORT, 19132),
    (ConfigKey.MAX_LOG_LENGTH, 100),  # cut log string. don't cut if value is None
    (ConfigKey.SERVER_GUID, None),  # use random value if value is None
    (ConfigKey.RESEND_TIME, 500),  # ms, interval that is greater than interval of ACK/NCK arrives
    (ConfigKey.BATCH_COMPRESS_THRESHOLD, 256),  # bytes, compress if exceeded
    (ConfigKey.SEED, 0),
    (ConfigKey.DIFFICULTY, 'NORMAL'),  # see mcpe.const.Difficulty
    (ConfigKey.RAIN_LEVEL, 0.0),
    (ConfigKey.LIGHTNING_LEVEL, 0.0),
    (ConfigKey.WORLD_NAME, 'PyMineHub'),
    (ConfigKey.GAME_MODE, 'SURVIVAL'),  # see mcpe.const.GameMode
)

_config = dict(__default_config)  # type: Dict[ConfigKey, Any]


def reset() -> None:
    _config.clear()
    _config.update(__default_config)
    set_config(server_guid=randrange(1 << (8 * 8)))  # long range


def set_config(**kwargs) -> None:
    _config.update(dict((ConfigKey[key.upper()], value) for key, value in kwargs.items()))


def get_value(key: ConfigKey) -> T:
    return _config[key]


reset()


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
