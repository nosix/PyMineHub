from typing import NamedTuple

from pyminehub.mcpe.const import PLAYER_EYE_HEIGHT, EntityType
from pyminehub.mcpe.geometry import Vector3

__all__ = [
    'EntitySpec',
    'PLAYER_ENTITY_SPEC',
    'ITEM_ENTITY_SPEC',
    'get_spec'
]


EntitySpec = NamedTuple('EntitySpec', [
    ('size', Vector3[float]),
    ('eye_height', float),
])


PLAYER_ENTITY_SPEC = EntitySpec(Vector3(1.0, 2.0, 1.0), PLAYER_EYE_HEIGHT)
ITEM_ENTITY_SPEC = EntitySpec(Vector3(0.5, 0.5, 0.5), 0.25)


_entity_specs = {
    EntityType.CHICKEN: EntitySpec(Vector3(0.3, 0.7, 0.3), 0.35)
}

_unsupported_entity_spec = EntitySpec(Vector3(1.0, 1.0, 1.0), 0.5)


def get_spec(entity_type: EntityType) -> EntitySpec:
    return _entity_specs.get(entity_type, _unsupported_entity_spec)
