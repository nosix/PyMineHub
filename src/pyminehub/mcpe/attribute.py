from typing import Optional

from pyminehub.mcpe.const import AttributeType
from pyminehub.mcpe.value import Attribute

__all__ = [
    'create_attribute'
]


_ATTRIBUTES = {
    AttributeType.HEALTH: (0.0, 20.0, 20.0),
    AttributeType.FOLLOW_RANGE: (0.0, 2048.0, 16.0),
    AttributeType.KNOCKBACK_RESISTANCE: (0.0, 1.0, 0.0),
    AttributeType.MOVEMENT: (0.0, 3.4028234663852886e+38, 0.10000000149011612),
    AttributeType.ATTACK_DAMAGE: (0.0, 3.4028234663852886e+38, 1.0),
    AttributeType.ABSORPTION: (0.0, 3.4028234663852886e+38, 0.0),
    AttributeType.PLAYER_SATURATION: (0.0, 20.0, 20.0),
    AttributeType.PLAYER_EXHAUSTION: (0.0, 5.0, 0.0),
    AttributeType.PLAYER_HUNGER: (0.0, 20.0, 20.0),
    AttributeType.PLAYER_LEVEL: (0.0, 24791.0, 0.0),
    AttributeType.PLAYER_EXPERIENCE: (0.0, 1.0, 0.0)
}


def create_attribute(attr_type: AttributeType, value: Optional[float]=None) -> Attribute:
    min_value, max_value, default_value = _ATTRIBUTES[attr_type]
    if value is None:
        value = default_value
    assert min_value <= value <= max_value
    return Attribute(min_value, max_value, value, default_value, 'minecraft:' + attr_type.value)
