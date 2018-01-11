from typing import NamedTuple as _NamedTuple

from pyminehub.mcpe.const import PLAYER_EYE_HEIGHT, EntityType
from pyminehub.mcpe.geometry import Vector3

EntitySpec = _NamedTuple('EntitySpec', [
    ('size', Vector3[float]),
    ('eye_height', float),
])


PLAYER_ENTITY_SPEC = EntitySpec(Vector3(1.0, 2.0, 1.0), PLAYER_EYE_HEIGHT)
ITEM_ENTITY_SPEC = EntitySpec(Vector3(0.5, 0.5, 0.5), 0.25)


_entity_specs = {
    EntityType.CHICKEN: EntitySpec(Vector3(0.3, 0.7, 0.3), 0.35)
}


def get_spec(entity_type: EntityType) -> EntitySpec:
    return _entity_specs[entity_type]
