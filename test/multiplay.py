import random
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, NamedTuple, Tuple

from action import ActionCommandMixin
from event import GameEventCommandMixin
from pyminehub.mcpe.const import ItemType, BlockType, EntityType
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEClient, EntityEvent, EntityInfo


class _Client(MCPEClient, ActionCommandMixin, GameEventCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self


def _move_position(position: Vector3[float]) -> Vector3[float]:
    return position + tuple(random.normalvariate(0, 1) for _ in range(3))


def move_player(client: _Client):
    position = _move_position(client.get_entity().position)
    client.move_player(
        *position,
        random.uniform(-180, 180),
        random.uniform(-180, 180),
        random.uniform(-180, 180)
    )


def put_item(client: _Client):
    face = random.choice(list(Face))
    position = client.get_entity().position
    block_position = _find_block(
        client, position, face, 5, lambda block_type: block_type is not BlockType.AIR)
    if block_position == position:
        return
    item_type = random.choice(list(ItemType))
    client.equip(
        item_type, 0,
        0
    )
    client.put_item(
        *block_position,
        item_type, 0,
        face.inverse,
        *tuple(random.uniform(0, 1) for _ in range(3))
    )


def break_block(client: _Client):
    face = random.choice(list(Face))
    position = client.get_entity().position
    block_position = _find_block(
        client, position, face, 5, lambda block_type: block_type is not BlockType.AIR)
    if block_position == position:
        return
    client.break_block(*block_position)


def _find_block(
        client: _Client,
        start: Vector3[float],
        face: Face,
        max_distance: int,
        equals_to: Callable[[BlockType], bool],
) -> Vector3[float]:
    if face is Face.NONE:
        return start
    position = start
    for distance in range(max_distance):
        position += face.direction
        block = client.get_block(*position, timeout=1)
        if block is None:
            return start
        if equals_to(block.type):
            return position
    return start


def spawn_mob(client: _Client):
    def entity_updated(event: EntityEvent, entity: EntityInfo) -> None:
        if event is EntityEvent.ADDED and entity.owner_runtime_id == client.entity_runtime_id:
            client.set_entity_event_listener(None)

    client.set_entity_event_listener(entity_updated)

    position = _move_position(client.get_entity().position)
    mob_type = random.choice(list(EntityType))
    if mob_type.value <= 57:
        client.spawn_mob(
            mob_type,
            *position,
            random.uniform(-180, 180),
            random.uniform(-180, 180)
        )


def move_mob(client: _Client):
    mob_id_list = tuple(e.entity_runtime_id for e in client.entities if e.owner_runtime_id == client.entity_runtime_id)
    if len(mob_id_list) == 0:
        return
    mob_id = random.choice(mob_id_list)
    entity = client.get_entity(mob_id)
    position = _move_position(entity.position)
    client.move_mob(
        mob_id,
        *position,
        random.uniform(-180, 180),
        random.uniform(-180, 180)
    )


Act = NamedTuple('Act', [
    ('callable', Callable[[_Client], None]),
    ('rate', int),
])


def select(acts: Tuple[Act, ...]) -> Act:
    total = sum(a.rate for a in acts)
    n = random.randrange(total)
    for a in acts:
        n -= a.rate
        if n < 0:
            return a
    raise AssertionError()


def run_client(name: str, lifespan: float, acts: Tuple[Act, ...]):
    start_time = time.time()
    with connect('127.0.0.1', player_name=name, client_factory=_Client, timeout=30) as client:
        while client.is_active and time.time() - start_time < lifespan:
            act = select(acts)
            act.callable(client)


def run_multiplay(max_workers: int, session_num: int, ave_lifespan: float, acts: Tuple[Act, ...]):
    with ProcessPoolExecutor(max_workers=max_workers) as e:
        for i in range(session_num):
            lifespan = random.normalvariate(ave_lifespan, 10)
            e.submit(run_client, 'Player-{}'.format(i), lifespan, acts)


if __name__ == '__main__':
    _acts = (
        Act(move_player, 40),
        Act(put_item, 20),
        Act(break_block, 5),
        Act(spawn_mob, 5),
        Act(move_mob, 30),
    )
    run_multiplay(20, 100, 60, _acts)
