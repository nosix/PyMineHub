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
from collections import namedtuple
from os.path import dirname
from unittest import TestCase

from pyminehub import config
from pyminehub.mcpe.network.codec import Codec
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

    def __init__(self, method_name):
        super().__init__(method_name)
        self._bytes_mask_enabled = True

    def enable_bytes_mask(self, value):
        self._bytes_mask_enabled = value

    def is_enabled_bytes_mask(self) -> bool:
        return self._bytes_mask_enabled

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


def interrupt_for_pycharm(exc: Exception, called, packet_info: str=None):
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


_ASCII_CHARS = set(c for c in range(0x20, 0x7f))
_ASCII_CHARS_FOR_DOUBLE_QUOTE = _ASCII_CHARS - {0x22, 0x5c, 0x5d}  # " - \
_ASCII_CHARS_FOR_SINGLE_QUOTE = _ASCII_CHARS - {0x27, 0x5c, 0x5d}  # ' - \

_BYTES_REGEXP_FOR_DOUBLE_QUOTE = re.compile(
    r'(b"[{}\-\\\]]*?")'.format(''.join(chr(c) for c in _ASCII_CHARS_FOR_DOUBLE_QUOTE)))
_BYTES_REGEXP_FOR_SINGLE_QUOTE = re.compile(
    r"(b'[{}\-\\\]]*?')".format(''.join(chr(c) for c in _ASCII_CHARS_FOR_SINGLE_QUOTE)))


class PacketAssertion:

    _MAX_BYTES_LEN = 16

    def __init__(self, stack_depth=3):
        called_line = traceback.format_stack()[-stack_depth]
        m = re.search(r'File "(.+)/.+\.py"', called_line)
        self.called_line = called_line.replace(m[1], '.', 1)
        self._data = None
        self._packet = None
        self._codec = None

    def record_decoded(self, data: bytes, packet: namedtuple, codec: Codec) -> None:
        self._data = data
        self._packet = packet
        self._codec = codec

    def has_record(self):
        return not (self._data is None or self._packet is None or self._codec is None)

    def is_correct_on(self, test_case: CodecTestCase, data: bytes) -> int:
        raise NotImplemented

    def verify_on(self, test_case: CodecTestCase) -> None:
        assert self.has_record()
        self.verify_children(test_case)
        data = self._codec.encode(self._packet)

        def reduce_bytes(m):
            bytes_data = eval(m[1])  # type: bytes
            length = len(bytes_data)
            return repr(bytes_data) if length <= self._MAX_BYTES_LEN else '[{} bytes]'.format(length)

        if test_case.is_enabled_bytes_mask():
            packet_str = str(self._packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
            packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(reduce_bytes, packet_str)
            packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(reduce_bytes, packet_str)
        else:
            packet_str = str(self._packet)
        try:
            test_case.assertEqual(
                self._data.hex(), data.hex(), '\n{}\n  {}'.format(self.called_line, packet_str))
            _logger.info('%s\n  -> %s\n%s', packet_str, self._data.hex(), self.called_line)
        except AssertionError as e:
            self.verify_error_hook(test_case, e, data)

    def verify_children(self, test_case: CodecTestCase) -> None:
        pass

    def verify_error_hook(self, test_case: CodecTestCase, exc: AssertionError, data: bytes) -> None:
        raise exc


class GamePacket(PacketAssertion):

    def __init__(self, packet_id: MCPEGamePacketID):
        """ Game packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__()
        self._packet_id = packet_id

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        packet = mcpe_game_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, MCPEGamePacketID(packet.id))
        test_case.assertEqual(len(data), context.length)
        self.record_decoded(data[:context.length], packet, mcpe_game_packet_codec)
        return context.length


class Batch(PacketAssertion):

    def __init__(self):
        """ Batch packet validator."""
        super().__init__()
        self._assertions = []

    def that_has(self, *game_packet: GamePacket):
        self._assertions.extend(game_packet)
        return self

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        packet = mcpe_packet_codec.decode(data, context)
        test_case.assertEqual(MCPEPacketID.BATCH, MCPEPacketID(packet.id))
        test_case.assertEqual(len(data), context.length)
        test_case.assertEqual(len(self._assertions), len(packet.payloads))
        packet_info = '  MCPE packet {}'.format(packet)
        for payload, assertion in zip(packet.payloads, self._assertions):
            try:
                assertion.is_correct_on(test_case, payload)
            except Exception as e:
                interrupt_for_pycharm(e, assertion.called_line, packet_info)
                message = '{} occurred while testing\n{}{}'.format(repr(e), assertion.called_line, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self.record_decoded(data[:context.length], packet, mcpe_packet_codec)
        return context.length

    def verify_children(self, test_case: CodecTestCase):
        for assertion in self._assertions:
            assertion.verify_on(test_case)

    def verify_error_hook(self, test_case: CodecTestCase, exc: AssertionError, data: bytes):
        print('There may be differences in compression results:', exc, file=sys.stderr)
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

    def that_has(self, batch: Batch):
        self._assertion = batch
        return self

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        capsule = raknet_capsule_codec.decode(data, context)
        test_case.assertEqual(self._capsule_id, RakNetCapsuleID(capsule.id))
        capsule_info = '  RakNet encapsulation {}'.format(capsule)
        if self._assertion is not None:
            try:
                self._assertion.is_correct_on(test_case, capsule.payload)
            except _WrappedException as e:
                message = '{}\n'.format(e.args[0], capsule_info)
                raise _WrappedException(e.exc, e.tb, message) from None
            except Exception as e:
                interrupt_for_pycharm(e, self._assertion.called, capsule_info)
                message = '{} occurred while testing\n{}'.format(repr(e), self._assertion.called, capsule_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        self.record_decoded(data[:context.length], capsule, raknet_capsule_codec)
        return context.length

    def verify_children(self, test_case: CodecTestCase):
        if self._assertion is not None:
            self._assertion.verify_on(test_case)


class RakNetPacket(PacketAssertion):

    def __init__(self, packet_id: RakNetPacketID):
        """ RakNet packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__()
        self._packet_id = packet_id
        self._assertions = []

    def that_has(self, *capsule: Capsule):
        self._assertions.extend(capsule)
        return self

    def _test_raknet_packet(self, test_case: CodecTestCase, data: bytes):
        assert self._packet_id is not None
        context = PacketCodecContext()
        packet = raknet_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, RakNetPacketID(packet.id), packet)
        test_case.assertEqual(len(data), context.length)
        self.record_decoded(data, packet, raknet_packet_codec)
        return context.length, packet

    def _test_raknet_encapsulation(self, test_case: CodecTestCase, packet: namedtuple):
        assert self.has_record()
        data = packet.payload
        packet_info = '  RakNet packet {}'.format(packet)
        payload_length = 0
        for assertion in self._assertions:
            try:
                payload_length += assertion.is_correct_on(test_case, data[payload_length:])
            except _WrappedException as e:
                message = '{}\n{}'.format(e.args[0], packet_info)
                raise _WrappedException(e.exc, e.tb, message) from None
            except Exception as e:
                interrupt_for_pycharm(e, assertion.called_line, packet_info)
                message = '{} occurred while testing\n{}{}'.format(repr(e), assertion.called_line, packet_info)
                raise _WrappedException(e, sys.exc_info()[2], message) from None
        test_case.assertEqual(len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        self._data = data
        try:
            length, packet = self._test_raknet_packet(test_case, data)
            self._test_raknet_encapsulation(test_case, packet)
            return length
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise _WrappedException(e.exc, e.tb, message) from None
        except Exception as e:
            interrupt_for_pycharm(e, self.called_line)
            message = '{} occurred while testing\n{}'.format(repr(e), self.called_line)
            raise _WrappedException(e, sys.exc_info()[2], message) from None

    def verify_children(self, test_case: CodecTestCase):
        for assertion in self._assertions:
            assertion.verify_on(test_case)


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

    def is_correct_on(self, test_case: CodecTestCase, and_verified_with_encoded_data=False):
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
