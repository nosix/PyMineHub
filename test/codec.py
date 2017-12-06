"""
Test cases for codec.

When debugging, execute `from codec import *` in REPL.
"""
import logging
import sys
import traceback
from binascii import unhexlify as unhex
from unittest import TestCase

from pyminehub.mcpe.network.codec import game_packet_codec as mcpe_game_packet_codec
from pyminehub.mcpe.network.codec import packet_codec as mcpe_packet_codec
from pyminehub.mcpe.network.packet import GamePacketID as MCPEGamePacketID
from pyminehub.mcpe.network.packet import PacketID as MCPEPacketID
from pyminehub.network.codec import PacketCodecContext
from pyminehub.raknet.codec import capsule_codec as raknet_capsule_codec
from pyminehub.raknet.codec import packet_codec as raknet_packet_codec
from pyminehub.raknet.encapsulation import CapsuleID as RakNetCapsuleID
from pyminehub.raknet.packet import PacketID as RakNetPacketID

_logger = logging.getLogger(__name__)


class _WrappedException(Exception):

    def __init__(self, exc: Exception, tb: traceback, message: str):
        super().__init__(message)
        self.exc = exc
        self.tb = tb


class GamePacket:

    def __init__(self, packet_id: MCPEGamePacketID, show_packet=False):
        """ Game packet validator.
        :param packet_id: expected packet ID
        :param show_packet: show packet information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._packet_id = packet_id
        self._data = None
        self._mcpe_game_packet = None
        self._show_packet = show_packet

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._mcpe_game_packet = mcpe_game_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, MCPEGamePacketID(self._mcpe_game_packet.id))
        test_case.assertEqual(len(data), context.length)
        self._data = data[:context.length]

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._mcpe_game_packet is not None
        data = mcpe_game_packet_codec.encode(self._mcpe_game_packet)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._mcpe_game_packet))
        if self._show_packet:
            _logger.info('%s\n  -> %s\n%s', self._mcpe_game_packet, self._data.hex(), self.called)


class Batch:

    def __init__(self, show_packet=False):
        """ Batch packet validator.
        :param show_packet: show packet information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._assertions = []
        self._data = None
        self._mcpe_packet = None
        self._show_packet = show_packet

    def that_has(self, game_packet: GamePacket):
        self._assertions.append(game_packet)
        return self

    def and_(self, game_packet: GamePacket):
        return self.that_has(game_packet)

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._mcpe_packet = mcpe_packet_codec.decode(data, context)
        test_case.assertEqual(MCPEPacketID.batch, MCPEPacketID(self._mcpe_packet.id))
        test_case.assertEqual(len(data), context.length)
        test_case.assertEqual(len(self._assertions), len(self._mcpe_packet.payloads))
        for payload, assertion in zip(self._mcpe_packet.payloads, self._assertions):
            try:
                assertion.is_correct_on(test_case, payload)
            except Exception as e:
                message = '{} occurred while testing\n{}  MCPE packet {}'.format(
                    repr(e), assertion.called, self._mcpe_packet)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self._data = data[:context.length]

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._mcpe_packet is not None
        data = mcpe_packet_codec.encode(self._mcpe_packet)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._mcpe_packet))
        for assertion in self._assertions:
            assertion.verify_on(test_case)
        if self._show_packet:
            _logger.info('%s\n  -> %s\n%s', self._mcpe_packet, self._data.hex(), self.called)


class Capsule:

    def __init__(self, capsule_id: RakNetCapsuleID, show_capsule=False):
        """ Encapsulation of RakNet packet validator.
        :param capsule_id: expected encapsulation ID
        :param show_capsule: show encapsulation information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._capsule_id = capsule_id
        self._assertion = None
        self._data = None
        self._capsule = None
        self._show_capsule = show_capsule

    def that_has(self, batch: Batch):
        self._assertion = batch
        return self

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._capsule = raknet_capsule_codec.decode(data, context)
        test_case.assertEqual(self._capsule_id, RakNetCapsuleID(self._capsule.id))
        if self._assertion is not None:
            try:
                self._assertion.is_correct_on(test_case, self._capsule.payload)
            except _WrappedException as e:
                message = '{}\n  RakNet encapsulation {}'.format(e.args[0], self._capsule)
                raise _WrappedException(e.exc, e.tb, message) from None
            except Exception as e:
                message = '{} occurred while testing\n{}  RakNet encapsulation {}'.format(
                    repr(e), self._assertion.called, self._capsule)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self._data = data[:context.length]
        return context.length

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._capsule is not None
        data = raknet_capsule_codec.encode(self._capsule)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._capsule))
        if self._assertion is not None:
            self._assertion.verify_on(test_case)
        if self._show_capsule:
            _logger.info('%s\n  -> %s\n%s', self._capsule, self._data.hex(), self.called)


class RakNetPacket:

    def __init__(self, packet_id: RakNetPacketID, show_packet=False):
        """ RakNet packet validator.
        :param packet_id: expected packet ID
        :param show_packet: show packet information when validator verify it
        """
        self.called = traceback.format_stack()[-2]
        self._packet_id = packet_id
        self._assertions = []
        self._data = None
        self._raknet_packet = None
        self._show_packet = show_packet

    def that_has(self, capsule: Capsule):
        self._assertions.append(capsule)
        return self

    def and_(self, capsule: Capsule):
        return self.that_has(capsule)

    def _test_raknet_packet(self, test_case: TestCase, data: bytes):
        assert self._packet_id is not None
        context = PacketCodecContext()
        self._raknet_packet = raknet_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, RakNetPacketID(self._raknet_packet.id), self._raknet_packet)
        test_case.assertEqual(len(data), context.length)

    def _test_raknet_encapsulation(self, test_case: TestCase):
        assert self._raknet_packet is not None
        data = self._raknet_packet.payload
        payload_length = 0
        for assertion in self._assertions:
            try:
                payload_length += assertion.is_correct_on(test_case, data[payload_length:])
            except _WrappedException as e:
                message = '{}\n  RakNet packet {}'.format(e.args[0], self._raknet_packet)
                raise _WrappedException(e.exc, e.tb, message) from None
            except Exception as e:
                message = '{} occurred while testing\n{}  RakNet packet {}'.format(
                    repr(e), assertion.called, self._raknet_packet)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        test_case.assertEqual(len(data), payload_length, data.hex())

    def is_correct_on(self, test_case: TestCase, data: bytes):
        self._data = data
        try:
            self._test_raknet_packet(test_case, data)
            self._test_raknet_encapsulation(test_case)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise test_case.failureException(message).with_traceback(e.tb) from None
        except Exception as e:
            message = '{} occurred while testing\n{}'.format(repr(e), self.called)
            raise test_case.failureException(message).with_traceback(sys.exc_info()[2]) from None

    def verify_on(self, test_case: TestCase):
        assert self._raknet_packet is not None
        data = raknet_packet_codec.encode(self._raknet_packet)
        test_case.assertEqual(self._data, data, '{}\n{}'.format(self.called, self._raknet_packet))
        for assertion in self._assertions:
            assertion.verify_on(test_case)
        if self._show_packet:
            _logger.info('%s\n  -> %s\n%s', self._raknet_packet, self._data.hex(), self.called)


class EncodedData:

    def __init__(self, data: str):
        """ Encoded data validator.

        :param data: data that decode to packet
        """
        self._data = unhex(data)
        self._assertion = None

    def is_(self, packet: RakNetPacket):
        self._assertion = packet
        return self

    def is_correct_on(self, test_case: TestCase, and_verify_encoded_data=False):
        self._assertion.is_correct_on(test_case, self._data)
        if and_verify_encoded_data:
            self._assertion.verify_on(test_case)


class TestDecode(TestCase):

    def setUp(self):
        _logger.setLevel(logging.INFO)
        self._handler = logging.StreamHandler(sys.stdout)
        _logger.addHandler(self._handler)

    def tearDown(self):
        _logger.addHandler(self._handler)

    def test_(self):
        assertion = EncodedData(
            '840400006000a000000000000000fe7801010800f7ff0702000000000000004e'
            '000a6000a801000001000000fe7801010900f6ff080600000000000000008100'
            '0f'
        ).is_(
            RakNetPacket(RakNetPacketID.custom_packet_4).that_has(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.play_status)
                    )
                )
            ).and_(
                Capsule(RakNetCapsuleID.reliable_ordered).that_has(
                    Batch().that_has(
                        GamePacket(MCPEGamePacketID.resource_packs_info)
                    )
                )
            )
        )
        assertion.is_correct_on(self, and_verify_encoded_data=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
