"""
Test cases for codec.

When debugging, execute `from codec import *` in REPL.
"""
import inspect
import logging
import re
import sys
import traceback
from binascii import unhexlify as unhex
from os.path import dirname
from unittest import TestCase

from pyminehub import config
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


class CodecTestCase(TestCase):

    def get_file_name(self, kind: str, ext='txt'):
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), kind, self._testMethodName, ext)

    def setUp(self):
        _logger.setLevel(logging.INFO)
        self._file_handler = logging.FileHandler(self.get_file_name('codec_result'), 'w')
        _logger.addHandler(self._file_handler)
        config.reset()

    def tearDown(self):
        _logger.removeHandler(self._file_handler)
        self._file_handler.close()


def interrupt_for_pycharm(exc: Exception, called, packet_info=None):
    if type(exc).__name__ == 'EqualsAssertionError':
        attrs = exc.__dict__
        if called is not None:
            if 'called' not in attrs:
                attrs['called'] = called
            if 'stack' not in attrs:
                attrs['stack'] = []
            if packet_info is not None:
                attrs['stack'].append(packet_info)
        else:
            messages = ['AssertionError occurred while testing', attrs['called'][:-1]]  # remove \n
            messages.extend(attrs['stack'])
            messages.append(attrs['msg'])
            attrs['msg'] = '\n'.join(messages)
        raise exc


class _WrappedException(Exception):

    def __init__(self, exc: Exception, tb: traceback, message: str):
        super().__init__(message)
        self.exc = exc
        self.tb = tb


class PacketAssertion:

    def __init__(self, stack_depth=3):
        called_line = traceback.format_stack()[-stack_depth]
        m = re.search(r'File "(.+)/.+\.py"', called_line)
        self.called_line = called_line.replace(m[1], '.', 1)

    def is_correct_on(self, test_case: TestCase, data: bytes):
        raise NotImplemented

    def verify_on(self, test_case: TestCase):
        raise NotImplemented


class GamePacket(PacketAssertion):

    def __init__(self, packet_id: MCPEGamePacketID):
        """ Game packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__()
        self._packet_id = packet_id
        self._data = None
        self._mcpe_game_packet = None

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._mcpe_game_packet = mcpe_game_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, MCPEGamePacketID(self._mcpe_game_packet.id))
        test_case.assertEqual(len(data), context.length)
        self._data = data[:context.length]

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._mcpe_game_packet is not None
        data = mcpe_game_packet_codec.encode(self._mcpe_game_packet)
        test_case.assertEqual(
            self._data.hex(), data.hex(), '\n{}\n  {}'.format(self.called_line, self._mcpe_game_packet))
        _logger.info('%s\n  -> %s\n%s', self._mcpe_game_packet, self._data.hex(), self.called_line)


class Batch(PacketAssertion):

    def __init__(self):
        """ Batch packet validator."""
        super().__init__()
        self._assertions = []
        self._data = None
        self._mcpe_packet = None

    def that_has(self, *game_packet: GamePacket):
        self._assertions.extend(game_packet)
        return self

    def is_correct_on(self, test_case: TestCase, data: bytes):
        context = PacketCodecContext()
        self._mcpe_packet = mcpe_packet_codec.decode(data, context)
        test_case.assertEqual(MCPEPacketID.BATCH, MCPEPacketID(self._mcpe_packet.id))
        test_case.assertEqual(len(data), context.length)
        test_case.assertEqual(len(self._assertions), len(self._mcpe_packet.payloads))
        for payload, assertion in zip(self._mcpe_packet.payloads, self._assertions):
            try:
                assertion.is_correct_on(test_case, payload)
            except Exception as e:
                packet_info = '  MCPE packet {}'.format(self._mcpe_packet)
                interrupt_for_pycharm(e, assertion.called_line, packet_info)
                message = '{} occurred while testing\n{}{}'.format(repr(e), assertion.called_line, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self._data = data[:context.length]

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._mcpe_packet is not None
        for assertion in self._assertions:
            assertion.verify_on(test_case)
        data = mcpe_packet_codec.encode(self._mcpe_packet)
        try:
            test_case.assertEqual(
                self._data.hex(), data.hex(), '\n{}\n  {}'.format(self.called_line, self._mcpe_packet))
            import re
            reduced = re.sub(
                r"bytearray\((b'.*')\)",
                lambda m: '[{} bytes]'.format(len(repr(m[1]))),
                str(self._mcpe_packet))
            _logger.info('%s\n  -> %s\n%s', reduced, self._data.hex(), self.called_line)
        except AssertionError as e:
            print('There may be differences in compression results:', e, file=sys.stderr)
            self.is_correct_on(test_case, data)
            self.verify_on(test_case)


class Capsule(PacketAssertion):

    def __init__(self, capsule_id: RakNetCapsuleID):
        """ Encapsulation of RakNet packet validator.
        :param capsule_id: expected encapsulation ID
        """
        super().__init__()
        self._capsule_id = capsule_id
        self._assertion = None
        self._data = None
        self._capsule = None

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
                packet_info = '  RakNet encapsulation {}'.format(self._capsule)
                interrupt_for_pycharm(e, self._assertion.called, packet_info)
                message = '{} occurred while testing\n{}'.format(repr(e), self._assertion.called, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self._data = data[:context.length]
        return context.length

    def verify_on(self, test_case: TestCase):
        assert self._data is not None and self._capsule is not None
        if self._assertion is not None:
            self._assertion.verify_on(test_case)
        data = raknet_capsule_codec.encode(self._capsule)
        test_case.assertEqual(self._data.hex(), data.hex(), '\n{}\n  {}'.format(self.called_line, self._capsule))
        _logger.info('%s\n  -> %s\n%s', self._capsule, self._data.hex(), self.called_line)


class RakNetPacket(PacketAssertion):

    def __init__(self, packet_id: RakNetPacketID):
        """ RakNet packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__()
        self._packet_id = packet_id
        self._assertions = []
        self._data = None
        self._raknet_packet = None

    def that_has(self, *capsule: Capsule):
        self._assertions.extend(capsule)
        return self

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
                packet_info = '  RakNet packet {}'.format(self._raknet_packet)
                interrupt_for_pycharm(e, assertion.called_line, packet_info)
                message = '{} occurred while testing\n{}{}'.format(repr(e), assertion.called_line, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        test_case.assertEqual(len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    def is_correct_on(self, test_case: TestCase, data: bytes):
        self._data = data
        try:
            self._test_raknet_packet(test_case, data)
            self._test_raknet_encapsulation(test_case)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise _WrappedException(e.exc, e.tb, message) from None
        except Exception as e:
            interrupt_for_pycharm(e, self.called_line)
            message = '{} occurred while testing\n{}'.format(repr(e), self.called_line)
            raise _WrappedException(e, sys.exc_info()[2], message) from None

    def verify_on(self, test_case: TestCase):
        assert self._raknet_packet is not None
        for assertion in self._assertions:
            assertion.verify_on(test_case)
        data = raknet_packet_codec.encode(self._raknet_packet)
        test_case.assertEqual(self._data.hex(), data.hex(), '\n{}\n  {}'.format(self.called_line, self._raknet_packet))
        _logger.info('%s\n  -> %s\n%s', self._raknet_packet, self._data.hex(), self.called_line)


class EncodedData:

    def __init__(self, data: str):
        """ Encoded data validator.

        :param data: data that decode to packet
        """
        self._data = unhex(data)
        self._assertion = None

    def is_(self, assertion: PacketAssertion):
        self._assertion = assertion
        return self

    def is_correct_on(self, test_case: TestCase, and_verified_with_encoded_data=False):
        try:
            self._assertion.is_correct_on(test_case, self._data)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise test_case.failureException(message).with_traceback(e.tb) from None
        except Exception as e:
            interrupt_for_pycharm(e, None)
            raise e
        if and_verified_with_encoded_data:
            self._assertion.verify_on(test_case)


class EncodedDataInFile(EncodedData):

    def __init__(self, test_case: CodecTestCase):
        """ Encoded data validator.

        Data is read from the file '{test_case_module_dir}/codec_data/{test_name}.txt'
        """
        with open(test_case.get_file_name('codec_data'), 'r') as file:
            data = ''.join(file.readlines())
        super().__init__(data)
