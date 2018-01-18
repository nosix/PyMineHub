import asyncio
from binascii import unhexlify, hexlify
from pickle import dumps, loads

from pyminehub.mcpe.action import ActionType, action_factory
from pyminehub.mcpe.command import *
from pyminehub.mcpe.network import MCPEClient
from pyminehub.mcpe.plugin.command import *
from pyminehub.mcpe.value import *
from pyminehub.raknet import ClientConnection


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

    def perform_action(self, action_or_type: Union[Action, ActionType], *args, **kwargs) -> None:
        action = action_factory.create(action_or_type, *args, **kwargs) \
            if isinstance(action_or_type, ActionType) else action_or_type
        data = hexlify(dumps(action)).decode()
        self.execute_command('/perform {}'.format(data))


def connect(
        server_host: str,
        port: int=None,
        loop: asyncio.AbstractEventLoop=None
) -> ClientConnection[ActionCommandClient]:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    :param loop: client run on this loop
    """
    from pyminehub.raknet import connect_raknet
    return connect_raknet(ActionCommandClient(), server_host, port, loop)


def start_console():
    import uuid

    def login():
        client.perform_action(action_factory.create(
            ActionType.LOGIN_PLAYER,
            uuid.uuid4()
        ))

    def chunk(x: str, z: str):
        client.perform_action(
            ActionType.REQUEST_CHUNK,
            (
                ChunkPositionWithDistance(0, ChunkPosition(int(x), int(z))),
            )
        )

    def entity(player_eid: str):
        client.perform_action(
            ActionType.REQUEST_ENTITY,
            int(player_eid)
        )

    def break_block(player_eid: str, x: str, y: str, z: str):
        client.perform_action(
            ActionType.BREAK_BLOCK,
            int(player_eid),
            Vector3(int(x), int(y), int(z))
        )

    def move_player(player_eid: str, x: str, y: str, z: str, pitch: str='0', yaw: str='0', head_yaw: str='0'):
        client.perform_action(
            ActionType.MOVE_PLAYER,
            int(player_eid),
            Vector3(float(x), float(y), float(z)),
            float(pitch), float(yaw), float(head_yaw),
            MoveMode.NORMAL,
            True,
            0
        )

    def put_item(player_eid: str, x: str, y: str, z: str, hotbar_slot: str, item: str, face: str= 'top'):
        client.perform_action(
            ActionType.PUT_ITEM,
            int(player_eid),
            Vector3(int(x), int(y), int(z)),
            Face[face.upper()],
            int(hotbar_slot),
            Item.create(ItemType[item.upper()], 1)
        )

    def equip(player_eid: str, inventory_slot: str, hotbar_slot: str, item: str, quantity: str='1'):
        client.perform_action(
            ActionType.EQUIP,
            int(player_eid),
            int(inventory_slot),
            int(hotbar_slot),
            Item.create(ItemType[item.upper()], int(quantity))
        )

    def logout(player_eid: str):
        client.perform_action(
            ActionType.LOGOUT_PLAYER,
            int(player_eid)
        )

    def receive():
        while True:
            packet = client.wait_response(0.1)
            if packet is None:
                break
            print(packet)

    commands = [
        login,
        chunk,
        entity,
        break_block,
        move_player,
        put_item,
        equip,
        logout
    ]

    command_map = dict((c.__name__, c) for c in commands)

    with connect('127.0.0.1') as client:
        while True:
            args = input('> ').split()
            name = args.pop(0)
            if name == 'exit':
                break
            try:
                command_map[name](*args)
                receive()
            except KeyError:
                print('Unknown command "{}".'.format(name))


if __name__ == '__main__':
    start_console()
