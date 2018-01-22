import asyncio
from binascii import unhexlify, hexlify
from pickle import loads, dumps
from unittest import TestCase

from pyminehub.config import set_config
from pyminehub.mcpe.action import action_factory, Action, ActionType
from pyminehub.mcpe.command import CommandRegistry, CommandContext, command
from pyminehub.mcpe.const import *
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.main.client import connect, MCPEClient
from pyminehub.mcpe.network import MCPEServerHandler
from pyminehub.mcpe.network.packet import EXTRA_DATA, GamePacketType, game_packet_factory
from pyminehub.mcpe.plugin.loader import PluginLoader
from pyminehub.mcpe.world import run as run_world
from pyminehub.raknet import raknet_server
from util.mock import MockDataStore


def _encode_action(action: Action) -> str:
    return hexlify(dumps(action)).decode()


def _decode_action(data: str) -> Action:
    return loads(unhexlify(data))


def _perform_action(client: MCPEClient, action: Action) -> None:
    client.execute_command('/perform {}'.format(_encode_action(action)))


class CommandProcessor:

    @command
    def ban(self, context: CommandContext, args: str) -> None:
        context.send_text('ban {}'.format(args))

    @command
    def perform(self, context: CommandContext, args: str) -> None:
        context.perform_action(_decode_action(args))


class ClientTestCase(TestCase):

    def setUp(self):
        set_config(spawn_mob=False)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        registry = CommandRegistry()
        registry.register_command_processor(CommandProcessor())
        store = MockDataStore()
        proxy = run_world(store, PluginLoader('', registry))
        self._handler = MCPEServerHandler(proxy, registry)

    def tearDown(self):
        asyncio.get_event_loop().close()

    def test_command_request(self):
        with raknet_server(self._handler) as server:
            with connect('127.0.0.1') as client:
                packet = client.wait_response(1)
                self.assertEqual(GamePacketType.TEXT, packet.type)

                client.execute_command('/ban taro')
                actual_packet = client.wait_response(1)
                expected_packet = game_packet_factory.create(
                    GamePacketType.TEXT,
                    EXTRA_DATA,
                    text_type=TextType.TRANSLATION,
                    needs_translation=False,
                    source=None,
                    message='ban taro',
                    parameters=(),
                    xbox_user_id=''
                )
                self.assertEqual(expected_packet, actual_packet)
            server.stop()

    def test_perform_action(self):
        with raknet_server(self._handler) as server:
            with connect('127.0.0.1') as client:
                packet = client.wait_response(1)
                self.assertEqual(GamePacketType.TEXT, packet.type)

                _perform_action(client, action_factory.create(
                    ActionType.SPAWN_MOB,
                    EntityType.CHICKEN,
                    Vector3(256.0, 65.0, 256.0),
                    0.0,
                    0.0,
                    None,
                    None
                ))

                actual_packet = client.wait_response(1)
                expected_packet = game_packet_factory.create(
                    GamePacketType.ADD_ENTITY,
                    EXTRA_DATA,
                    entity_unique_id=2,
                    entity_runtime_id=2,
                    entity_type=EntityType.CHICKEN,
                    position=Vector3(256.0, 63.0, 256.0),  # height is adjusted
                    motion=Vector3(0.0, 0.0, 0.0),
                    pitch=0.0,
                    yaw=0.0,
                    attributes=(),
                    metadata=(),
                    links=()
                )
                self.assertEqual(expected_packet, actual_packet)

                _perform_action(client, action_factory.create(
                    ActionType.MOVE_MOB,
                    2,
                    Vector3(257.0, 63.0, 254.0),
                    45.0,
                    90.0
                ))

                actual_packet = client.wait_response(1)
                expected_packet = game_packet_factory.create(
                    GamePacketType.MOVE_ENTITY,
                    EXTRA_DATA,
                    entity_runtime_id=2,
                    position=Vector3(257.0, 63.0, 254.0),
                    pitch=45.0,
                    head_yaw=0.0,
                    yaw=90.0,
                    on_ground=True,
                    teleported=False
                )
                self.assertEqual(expected_packet, actual_packet)
            server.stop()


if __name__ == '__main__':
    import unittest
    unittest.main()
