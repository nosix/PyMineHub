from collections import defaultdict
from typing import Dict

from pyminehub.mcpe.network.packet import GamePacketType
from pyminehub.raknet import Reliability

UNRELIABLE = Reliability(False, None)
RELIABLE = Reliability(True, None)
DEFAULT_CHANEL = Reliability(True, 0)


def _init_reliability(reliabilities: Dict[GamePacketType, Reliability]) -> Dict[GamePacketType, Reliability]:
    d = defaultdict(lambda: DEFAULT_CHANEL)
    d.update(reliabilities)
    return d


RELIABILITY_DICT = _init_reliability({})
