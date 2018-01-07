from typing import NamedTuple as _NamedTuple

from pyminehub.mcpe.geometry import Vector3

EntitySpec = _NamedTuple('EntitySpec', [
    ('size', Vector3[float]),
    ('eye_height', float),
])


PLAYER_ENTITY_SPEC = EntitySpec(Vector3(1.0, 2.0, 1.0), 1.625)
ITEM_ENTITY_SPEC = EntitySpec(Vector3(0.5, 0.5, 0.5), 0.25)
