from binascii import hexlify
from pickle import dumps
from typing import Optional, Tuple, Union

from pyminehub.mcpe.action import Action, ActionType, action_factory
from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.const import MoveMode, ItemType, EntityType
from pyminehub.mcpe.geometry import Vector3, Face, ChunkPosition, ChunkPositionWithDistance, to_local_position
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEClient, EntityInfo, EntityEvent
from pyminehub.mcpe.value import *


class ActionCommandMixin:

    @property
    def client(self) -> MCPEClient:
        raise NotImplementedError()

    def _player_eid(self, player_eid: Optional[EntityRuntimeID]=None) -> EntityRuntimeID:
        return player_eid if player_eid is not None else self.client.entity_runtime_id

    def perform_action(self, action_or_type: Union[Action, ActionType], *args, **kwargs) -> None:
        action = action_factory.create(action_or_type, *args, **kwargs) \
            if isinstance(action_or_type, ActionType) else action_or_type
        data = hexlify(dumps(action)).decode()
        self.client.execute_command('/perform {}'.format(data))

    def request_full_chunk(self, east: float, south: float):
        self.perform_action(
            ActionType.REQUEST_CHUNK,
            (
                ChunkPositionWithDistance(0, ChunkPosition.at(Vector3(east, 0, south))),
            ),
            self._player_eid()
        )

    def request_entity_list(self):
        self.perform_action(
            ActionType.REQUEST_ENTITY,
            self._player_eid()
        )

    def get_height(self, east: float, south: float, timeout: float=0) -> Optional[int]:
        chunk, position_in_chunk = self._get_chunk(east, 0, south, timeout)
        return chunk.get_height(*position_in_chunk.to_2d()) if chunk is not None else None

    def get_block(self, east: float, height: float, south: float, timeout: float=0) -> Optional[Block]:
        chunk, position_in_chunk = self._get_chunk(east, height, south, timeout)
        return chunk.get_block(position_in_chunk) if chunk is not None else None

    def _get_chunk(
            self, east: float, height: float, south: float, timeout: float=0
    ) -> Tuple[Optional[Chunk], Vector3[int]]:
        position = Vector3(east, height, south).astype(int)
        position_in_chunk = to_local_position(position)
        if self._sync_chunk_by_position(position, timeout):
            return self.client.latest_chunk.chunk, position_in_chunk
        else:
            return None, position_in_chunk

    def _sync_chunk_by_position(self, position: Vector3[int], timeout: float=0) -> bool:
        chunk_position = ChunkPosition.at(position)
        if self.client.latest_chunk.position != chunk_position:
            self.request_full_chunk(*position.to_2d())
            self.client.wait_response(timeout)
        return self.client.latest_chunk.position == chunk_position

    def move_player(
            self,
            east: float, height: float, south: float,
            pitch: float=0.0, yaw: float=0.0, head_yaw: float=0.0,
            is_teleport: bool=False,
            player_eid: Optional[EntityRuntimeID]=None
    ):
        self.perform_action(
            ActionType.MOVE_PLAYER,
            self._player_eid(player_eid),
            Vector3(east, height, south),
            pitch, yaw, head_yaw,
            MoveMode.TELEPORT if is_teleport else MoveMode.NORMAL,
            True,
            0,
            True
        )

    def break_block(
            self,
            east: int, height: int, south: int,
            player_eid: Optional[EntityRuntimeID]=None
    ):
        self.perform_action(
            ActionType.BREAK_BLOCK,
            self._player_eid(player_eid),
            Vector3(east, height, south).astype(int)
        )

    def equip(
            self,
            item_type: ItemType, item_data: int,
            inventory_slot: int,
            hotbar_slot: int=0,
            quantity: int=1,
            player_eid: Optional[EntityRuntimeID]=None
    ):
        item = Item.create(item_type, quantity, item_data)
        self.perform_action(
            ActionType.SET_INVENTORY,
            self._player_eid(player_eid),
            inventory_slot,
            item
        )
        self.perform_action(
            ActionType.EQUIP,
            self._player_eid(player_eid),
            inventory_slot,
            hotbar_slot,
            item
        )

    def put_item(
            self,
            east: int, height: int, south: int,
            item_type: ItemType, item_data: int,
            face: Face=Face.TOP,
            click_east: float=0.5, click_height: float=0.5, click_south: float=0.5,
            hotbar_slot: int=0,
            player_eid: Optional[EntityRuntimeID]=None
    ):
        def revise(value: float, direction: int) -> float:
            if direction == 1:
                return 1.0
            elif direction == -1:
                return 0.0
            else:
                return value
        click_east = revise(click_east, face.direction.x)
        click_height = revise(click_height, face.direction.y)
        click_south = revise(click_south, face.direction.z)
        self.perform_action(
            ActionType.PUT_ITEM,
            self._player_eid(player_eid),
            Vector3(east, height, south).astype(int),
            Vector3(click_east, click_height, click_south),
            face,
            hotbar_slot,
            Item.create(item_type, 1, item_data)
        )

    def spawn_mob(
            self,
            entity_type: EntityType,
            east: float, height: float, south: float,
            pitch: float=0.0, yaw: float=0.0,
            name: Optional[str]=None
    ):
        self.perform_action(
            ActionType.SPAWN_MOB,
            entity_type,
            Vector3(east, height, south),
            pitch,
            yaw,
            name,
            self.handler.entity_runtime_id
        )

    def move_mob(
            self,
            mob_eid: EntityRuntimeID,
            east: float, height: float, south: float,
            pitch: float=0.0, yaw: float=0.0
    ):
        self.perform_action(
            ActionType.MOVE_MOB,
            mob_eid,
            Vector3(east, height, south),
            pitch,
            yaw
        )


class ActionCommandClient(MCPEClient, ActionCommandMixin):

    @property
    def client(self) -> MCPEClient:
        return self


if __name__ == '__main__':
    with connect('127.0.0.1', player_name='Taro', client_factory=ActionCommandClient) as _client:
        print('Number of entities', len(_client.entities))

        _client.move_player(10.0, 0.0, 10.0, is_teleport=True)
        _client.wait_response(timeout=1)
        print('Player', _client.get_entity())

        _position = _client.get_entity().position + (1, 0, -1)

        _client.move_player(*_position)
        _client.wait_response(timeout=1)
        print('Player', _client.get_entity())

        _height = _client.get_height(*_position.to_2d())
        print('Height', _height, 'at', _position.to_2d())

        _x = _position.x + 1

        _block_position = _position.copy(x=_x, y=_height - 1)
        _block = _client.get_block(*_block_position)
        print(_block, 'at', _block_position)

        _block_position = _position.copy(x=_x, y=_height)
        _block = _client.get_block(*_block_position)
        print(_block, 'at', _block_position)

        _client.equip(ItemType.DIRT, item_data=0, inventory_slot=0)
        _client.put_item(*_position.copy(x=_x, y=_height - 1), ItemType.DIRT, item_data=0)
        _client.wait_response(timeout=1)

        _block = _client.get_block(*_block_position)
        print(_block, 'at', _block_position)

        _client.break_block(*_block_position)

        _block = _client.get_block(*_block_position)
        print(_block, 'at', _block_position)

        _client.request_entity_list()
        _client.wait_response(timeout=1)
        print('Number of entities', len(_client.entities))

        _mob_eid = 0

        def entity_updated(event: EntityEvent, entity: EntityInfo) -> None:
            print('Listen', event, entity)
            global _mob_eid
            if event is EntityEvent.ADDED and entity.owner_runtime_id == _client.entity_runtime_id:
                _mob_eid = entity.entity_runtime_id

        _client.set_entity_event_listener(entity_updated)

        _client.spawn_mob(EntityType.CHICKEN, 10.0, 10.0, 10.0)
        _client.wait_response(timeout=1)
        print('Number of entities', len(_client.entities))

        _client.move_mob(_mob_eid, 5.0, 63.0, 1.0)
        _client.wait_response(timeout=1)
        print(_client.get_entity(_mob_eid))
