from binascii import unhexlify, hexlify
from pickle import dumps, loads

from pyminehub.mcpe.action import ActionType, action_factory
from pyminehub.mcpe.command import *
from pyminehub.mcpe.network import MCPEClient
from pyminehub.mcpe.network.packet import GamePacketType
from pyminehub.mcpe.plugin.command import *
from pyminehub.mcpe.value import *
from pyminehub.raknet import ClientConnection, connect_raknet


class ActionCommandProcessor:

    @command
    def perform(self, context: CommandContext, args: str) -> None:
        """Perform action in the world."""
        action = loads(unhexlify(args))
        context.perform_action(action)


class ActionCommandPlugin(ExtraCommandPlugin):

    @property
    def processor(self) -> Any:
        return ActionCommandProcessor()


class ActionCommandClient(MCPEClient):

    def _player_eid(self, player_eid: Optional[EntityRuntimeID]) -> EntityRuntimeID:
        return player_eid if player_eid is not None else self.handler.entity_runtime_id

    def perform_action(self, action_or_type: Union[Action, ActionType], *args, **kwargs) -> None:
        action = action_factory.create(action_or_type, *args, **kwargs) \
            if isinstance(action_or_type, ActionType) else action_or_type
        data = hexlify(dumps(action)).decode()
        self.execute_command('/perform {}'.format(data))

    def chunk(self, x: int, z: int):
        self.perform_action(
            ActionType.REQUEST_CHUNK,
            (
                ChunkPositionWithDistance(0, ChunkPosition(x, z)),
            )
        )

    def entity(self, player_eid: Optional[EntityRuntimeID]=None):
        self.perform_action(
            ActionType.REQUEST_ENTITY,
            self._player_eid(player_eid)
        )

    def move(
            self,
            east: float, south: float, height: float,
            pitch: float=0.0, yaw: float=0.0, head_yaw: float=0.0,
            player_eid: Optional[EntityRuntimeID]= None
    ):
        self.perform_action(
            ActionType.MOVE_PLAYER,
            self._player_eid(player_eid),
            Vector3(east, height, south),
            pitch, yaw, head_yaw,
            MoveMode.NORMAL,
            True,
            0
        )

    def break_block(self, east: int, south: int, height: int, player_eid: Optional[EntityRuntimeID]=None):
        self.perform_action(
            ActionType.BREAK_BLOCK,
            self._player_eid(player_eid),
            Vector3(east, height, south)
        )

    def put_item(
            self,
            east: int, south: int, height: int,
            hotbar_slot: int,
            item_type: ItemType,
            face: Face=Face.TOP,
            player_eid: Optional[EntityRuntimeID]=None
    ):
        self.perform_action(
            ActionType.PUT_ITEM,
            self._player_eid(player_eid),
            Vector3(east, height, south),
            face,
            hotbar_slot,
            Item.create(item_type, 1)
        )

    def equip(
            self,
            inventory_slot: int, hotbar_slot: int,
            item_type: ItemType,
            quantity: int=1,
            player_eid: Optional[EntityRuntimeID]=None
    ):
        self.perform_action(
            ActionType.EQUIP,
            self._player_eid(player_eid),
            inventory_slot,
            hotbar_slot,
            Item.create(item_type, quantity)
        )

    def spawn_mob(
            self,
            entity_type: EntityType,
            east: float, south: float, height: float,
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
            east: float, south: float, height: float,
            pitch: float=0.0, yaw: float=0.0
    ):
        self.perform_action(
            ActionType.MOVE_MOB,
            mob_eid,
            Vector3(east, height, south),
            pitch,
            yaw
        )


def connect(
        server_host: str,
        port: int=None
) -> ClientConnection[ActionCommandClient]:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    """
    return connect_raknet(ActionCommandClient(), server_host, port)


if __name__ == '__main__':
    with connect('127.0.0.1') as _client:
        _client.wait_response()  # Login text
        _move = 0.0
        _client.spawn_mob(EntityType.CHICKEN, 256.0, 256.0, 65.0)
        while True:
            _packet = _client.wait_response()
            if _packet.type == GamePacketType.ADD_ENTITY:
                for _metadata in _packet.metadata:
                    if _metadata.key == EntityMetaDataKey.OWNER_EID and \
                            _metadata.value == _client.handler.entity_runtime_id:
                        mob_runtime_id = _packet.entity_runtime_id
                        break
                else:
                    continue
                break
        while True:
            _move += 0.5
            _client.move_mob(mob_runtime_id, 256.0, 256.6 + _move, 65.0)
