import asyncio
from unittest import TestCase

from pyminehub.mcpe.command import CommandRegistry, CommandContext, command
from pyminehub.mcpe.const import *
from pyminehub.mcpe.main.client import connect
from pyminehub.mcpe.network import MCPEServerHandler, MCPEClient
from pyminehub.mcpe.network.packet import EXTRA_DATA, GamePacketType, game_packet_factory
from pyminehub.raknet import run_raknet
from util.mock import MockWorldProxy


class CommandProcessor:

    @command
    def ban(self, context: CommandContext, args: str) -> None:
        context.send_text('ban {}'.format(args))


class ClientTestCase(TestCase):

    def test_command_request(self):
        import logging
        logging.basicConfig(level=logging.INFO)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        registry = CommandRegistry()
        registry.register_command_processor(CommandProcessor())

        with run_raknet(loop, MCPEServerHandler(MockWorldProxy(), registry)) as server:
            with connect('127.0.0.1', loop=loop) as client:  # type: MCPEClient
                client.execute_command('/ban taro')
                actual_packet = client.wait_response()
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
        loop.close()


if __name__ == '__main__':
    import unittest
    unittest.main()
