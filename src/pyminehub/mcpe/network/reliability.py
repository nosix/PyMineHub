from collections import defaultdict
from typing import Dict

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.network.packet import GamePacketType
from pyminehub.network.handler import Reliability

__all__ = [
    'UNRELIABLE',
    'RELIABLE',
    'DEFAULT_CHANEL',
    'RELIABILITY_DICT'
]


UNRELIABLE = Reliability(False, None)
RELIABLE = Reliability(True, None)
DEFAULT_CHANEL = Reliability(True, 0)


def _init_reliability(reliabilities: Dict[GamePacketType, Reliability]) -> Dict[GamePacketType, Reliability]:
    d = defaultdict(lambda: DEFAULT_CHANEL)
    d.update(reliabilities)
    return d


RELIABILITY_DICT = _init_reliability(
    {
        GamePacketType.MOVE_PLAYER: UNRELIABLE,
        GamePacketType.MOVE_ENTITY: UNRELIABLE,
    }
    if get_value(ConfigKey.ROUGH_MOVE) else {})
