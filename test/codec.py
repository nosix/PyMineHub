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
from typing import Callable, Union, Any
from unittest import TestCase

from pyminehub import config
from pyminehub.mcpe.network.codec import connection_packet_codec
from pyminehub.mcpe.network.codec import game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketID
from pyminehub.mcpe.network.packet import GamePacketID
from pyminehub.network.codec import Codec
from pyminehub.network.codec import PacketCodecContext
from pyminehub.raknet.codec import capsule_codec as raknet_capsule_codec
from pyminehub.raknet.codec import raknet_packet_codec as raknet_packet_codec
from pyminehub.raknet.encapsulation import CapsuleID
from pyminehub.raknet.packet import RakNetPacketID

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

    def __init__(self, packet_type: str, stack_depth=3):
        called_line = traceback.format_stack()[-stack_depth]
        m = re.search(r'File "(.+)/.+\.py"', called_line)
        self.called_line = called_line.replace(m[1], '.', 1)
        self._packet_type = packet_type
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
        try:
            packet_str = self._get_packet_str(test_case)
            message = '\n{}\n  {}'.format(self.called_line, packet_str)
            test_case.assertEqual(self._data.hex(), data.hex(), message)
            self._log(packet_str)
        except AssertionError as e:
            self.verify_error_hook(test_case, e, data, self.called_line)

    def verify_children(self, test_case: CodecTestCase) -> None:
        pass

    def verify_error_hook(self, test_case: CodecTestCase, exc: AssertionError, data: bytes, called_line: str) -> None:
        raise exc

    def try_child_assertion(self, assertion_method: Callable[..., None], *args) -> Any:
        assert self.has_record()
        # noinspection PyUnresolvedReferences
        assertion = assertion_method.__self__
        packet_info = '  {} {}'.format(self._packet_type, self._packet)
        try:
            return assertion_method(*args)
        except _WrappedException as e:
            message = '{}\n'.format(e.args[0], packet_info)
            raise _WrappedException(e.exc, e.tb, message) from None
        except Exception as e:
            interrupt_for_pycharm(e, assertion.called_line, packet_info)
            message = '{} occurred while testing\n{}'.format(repr(e), assertion.called_line, packet_info)
            raise _WrappedException(e, sys.exc_info()[2], message) from None

    def _summarize_bytes(self, m: re.match) -> str:
        bytes_data = eval(m[1])  # type: bytes
        length = len(bytes_data)
        return repr(bytes_data) if length <= self._MAX_BYTES_LEN else '[{} bytes]'.format(length)

    def _get_packet_str(self, test_case: CodecTestCase) -> str:
        if test_case.is_enabled_bytes_mask():
            packet_str = str(self._packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
            packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(self._summarize_bytes, packet_str)
            packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(self._summarize_bytes, packet_str)
        else:
            packet_str = str(self._packet)
        return packet_str

    def _log(self, packet_str: str) -> None:
        _logger.info('%s\n  -> %s\n%s', packet_str, self._data.hex(), self.called_line)

    def print_packet(self, test_case: CodecTestCase) -> None:
        self._log(self._get_packet_str(test_case))


class GamePacket(PacketAssertion):

    def __init__(self, packet_id: GamePacketID):
        """ Game packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__('Game packet')
        self._packet_id = packet_id

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        packet = game_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, GamePacketID(packet.id))
        test_case.assertEqual(len(data), context.length)
        self.record_decoded(data[:context.length], packet, game_packet_codec)
        return context.length


class ConnectionPacket(PacketAssertion):

    def __init__(self, packet_id: ConnectionPacketID):
        """ Connection packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__('Connection packet')
        self._packet_id = packet_id

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        packet = connection_packet_codec.decode(data, context)
        test_case.assertEqual(self._packet_id, ConnectionPacketID(packet.id))
        test_case.assertEqual(len(data), context.length)
        self.record_decoded(data[:context.length], packet, connection_packet_codec)
        return context.length


class Batch(PacketAssertion):

    def __init__(self):
        """ Batch packet validator."""
        super().__init__('Batch packet')
        self._assertions = []

    def that_has(self, *game_packet: GamePacket):
        self._assertions.extend(game_packet)
        return self

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        packet = connection_packet_codec.decode(data, context)
        test_case.assertEqual(ConnectionPacketID.BATCH, ConnectionPacketID(packet.id))
        test_case.assertEqual(len(data), context.length)
        test_case.assertEqual(len(self._assertions), len(packet.payloads))
        self.record_decoded(data[:context.length], packet, connection_packet_codec)
        for payload, assertion in zip(packet.payloads, self._assertions):
            self.try_child_assertion(assertion.is_correct_on, test_case, payload)
        return context.length

    def verify_children(self, test_case: CodecTestCase):
        for assertion in self._assertions:
            self.try_child_assertion(assertion.verify_on, test_case)

    def verify_error_hook(self, test_case: CodecTestCase, exc: AssertionError, data: bytes, called_line: str):
        print('Warning: There may be differences in compression results:\n', called_line, file=sys.stderr)
        self.is_correct_on(test_case, data)
        self.verify_on(test_case)

    def print_packet(self, test_case: CodecTestCase):
        for assertion in self._assertions:
            assertion.print_packet(test_case)
        super().print_packet(test_case)


class Capsule(PacketAssertion):

    def __init__(self, capsule_id: CapsuleID):
        """ Encapsulation of RakNet packet validator.
        :param capsule_id: expected encapsulation ID
        """
        super().__init__('Encapsulation')
        self._capsule_id = capsule_id
        self._assertion = None

    def that_has(self, packet: Union[ConnectionPacket, Batch]):
        self._assertion = packet
        return self

    def is_correct_on(self, test_case: CodecTestCase, data: bytes):
        context = PacketCodecContext()
        capsule = raknet_capsule_codec.decode(data, context)
        test_case.assertEqual(self._capsule_id, CapsuleID(capsule.id))
        self.record_decoded(data[:context.length], capsule, raknet_capsule_codec)
        if self._assertion is not None:
            self.try_child_assertion(self._assertion.is_correct_on, test_case, capsule.payload)
        return context.length

    def verify_children(self, test_case: CodecTestCase):
        if self._assertion is not None:
            self.try_child_assertion(self._assertion.verify_on, test_case)


class RakNetPacket(PacketAssertion):

    def __init__(self, packet_id: RakNetPacketID):
        """ RakNet packet validator.
        :param packet_id: expected packet ID
        """
        super().__init__('RakNet packet')
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
        payload_length = 0
        for assertion in self._assertions:
            payload_length += self.try_child_assertion(assertion.is_correct_on, test_case, data[payload_length:])
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
            self.try_child_assertion(assertion.verify_on, test_case)


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

    @staticmethod
    def _try_child_assertion(test_case: CodecTestCase, assertion_method: Callable[..., None], *args):
        try:
            assertion_method(*args)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise test_case.failureException(message).with_traceback(e.tb) from None
        except Exception as e:
            interrupt_for_pycharm(e, None)
            raise e

    def is_correct_on(self, test_case: CodecTestCase, and_verified_with_encoded_data=False):
        self._try_child_assertion(test_case, self._assertion.is_correct_on, test_case, self._data)
        if and_verified_with_encoded_data:
            self._try_child_assertion(test_case, self._assertion.verify_on, test_case)
        else:
            self._assertion.print_packet(test_case)


class EncodedDataInFile(EncodedData):

    def __init__(self, test_case: CodecTestCase):
        """ Encoded data validator.

        Data is read from the file '{test_case_module_dir}/codec_data/{test_name}.txt'
        """
        with open(test_case.get_file_name('codec_data'), 'r') as file:
            data = ''.join(file.readlines())
        super().__init__(data)
