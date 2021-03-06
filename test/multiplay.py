import multiprocessing
import random
import time
from typing import Callable, NamedTuple, Tuple

from action import ActionCommandMixin
from event import GameEventCommandMixin
from pyminehub.mcpe.const import ItemType, BlockType, EntityType
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEClient, EntityEvent, EntityInfo


class _Client(MCPEClient, ActionCommandMixin, GameEventCommandMixin):

    def __init__(self, player_name: str, locale: str) -> None:
        super().__init__(player_name, locale)
        self.set_entity_event_listener(self._entity_updated)
        self._num_of_waiting = 0

    @property
    def client(self) -> MCPEClient:
        return self

    @property
    def num_of_waiting(self) -> int:
        return self._num_of_waiting

    def _entity_updated(self, event: EntityEvent, entity: EntityInfo) -> None:
        if event is EntityEvent.ADDED and entity.owner_runtime_id == self.entity_runtime_id:
            self._num_of_waiting -= 1

    def increment_waiting(self) -> None:
        self._num_of_waiting += 1


def _move_position(position: Vector3[float]) -> Vector3[float]:
    return position + tuple(random.normalvariate(0, 1) for _ in range(3))


def move_player(client: _Client):
    position = _move_position(client.get_entity().position)
    client.move_player(
        *position,
        random.uniform(-180, 180),
        random.uniform(-180, 180),
        random.uniform(-180, 180),
        on_ground=True
    )


def put_item(client: _Client):
    face = random.choice(list(Face))
    position = client.get_entity().position
    block_position = _find_block(
        client, position, face, 5, lambda block_type: block_type is not BlockType.AIR)
    if block_position == position:
        return
    item_type = random.choice(list(ItemType))
    if item_type is ItemType.AIR:
        return
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
    mob_type = random.choice(list(EntityType))
    if mob_type.value <= 57:
        client.increment_waiting()

        position = _move_position(client.get_entity().position)
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
        random.uniform(-180, 180),
        on_ground=True
    )


def remove_all_mobs(client: _Client):
    retry = 0
    while client.num_of_waiting > 0:
        before = client.num_of_waiting
        client.wait_response()
        if retry % 100 == 0 and retry != 0:
            print('Waited response', retry, 'times to remove all mobs.')
        if client.num_of_waiting == before:
            retry += 1
        else:
            retry = 0
    mob_id_list = tuple(e.entity_runtime_id for e in client.entities if e.owner_runtime_id == client.entity_runtime_id)
    for mob_id in mob_id_list:
        client.remove_mob(mob_id)


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
    try:
        with connect('127.0.0.1', player_name=name, client_factory=_Client, timeout=30) as client:
            try:
                while client.is_active and time.time() - start_time < lifespan:
                    act = select(acts)
                    act.callable(client)
            finally:
                remove_all_mobs(client)
    except KeyboardInterrupt:
        pass


def run_multiplay(max_workers: int, session_num: int, ave_lifespan: float, acts: Tuple[Act, ...]):
    def start_task(i: int):
        lifespan = random.normalvariate(ave_lifespan, 10)
        return pool.apply_async(run_client, ('Player-{}'.format(i), lifespan, acts))

    with multiprocessing.Pool(max_workers) as pool:
        tasks = tuple(start_task(i) for i in range(session_num))
        try:
            for task in tasks:
                task.wait()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    _acts = (
        Act(move_player, 40),
        Act(put_item, 20),
        Act(break_block, 5),
        Act(spawn_mob, 5),
        Act(move_mob, 30),
    )
    run_multiplay(20, 100, 60, _acts)
