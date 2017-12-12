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
from pyminehub.network.packet import Packet
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


class PacketVisitor:

    def is_enabled_bytes_mask(self) -> bool:
        raise NotImplementedError()

    def visit_decode_raknet_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        raise NotImplementedError()

    def visit_decode_capsules(self, data: bytes, payload_length: int) -> None:
        raise NotImplementedError()

    def visit_decode_capsule_task(
            self, capsule: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        raise NotImplementedError()

    def visit_decode_connection_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        raise NotImplementedError()

    def visit_decode_batch_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext,
            expected_payloads_num: int, *args, **kwargs) -> None:
        raise NotImplementedError()

    def visit_decode_game_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        raise NotImplementedError()

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        raise NotImplementedError()


class PacketAssertion(PacketVisitor):

    def __init__(self, test_case: CodecTestCase) -> None:
        self._test_case = test_case

    def is_enabled_bytes_mask(self) -> bool:
        return self._test_case.is_enabled_bytes_mask()

    # noinspection PyMethodOverriding
    def visit_decode_raknet_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, packet_id: RakNetPacketID) -> None:
        self._test_case.assertEqual(packet_id, RakNetPacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)

    def visit_decode_capsules(self, data: bytes, payload_length: int) -> None:
        self._test_case.assertEqual(len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    # noinspection PyMethodOverriding
    def visit_decode_capsule_task(
            self, capsule: Packet, data: bytes, context: PacketCodecContext, capsule_id: CapsuleID) -> None:
        self._test_case.assertEqual(capsule_id, CapsuleID(capsule.id))

    # noinspection PyMethodOverriding
    def visit_decode_connection_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, packet_id: ConnectionPacketID) -> None:
        self._test_case.assertEqual(packet_id, ConnectionPacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)

    # noinspection PyMethodOverriding
    def visit_decode_batch_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext,
            expected_payloads_num: int, packet_id: ConnectionPacketID) -> None:
        self._test_case.assertEqual(packet_id, ConnectionPacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)
        self._test_case.assertEqual(expected_payloads_num, len(packet.payloads))

    # noinspection PyMethodOverriding
    def visit_decode_game_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, packet_id: GamePacketID) -> None:
        self._test_case.assertEqual(packet_id, GamePacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        self._test_case.assertEqual(original_data.hex(), encoded_data.hex(), packet_info)


class PacketAnalyzer:

    _MAX_BYTES_LEN = 16

    def __init__(self, packet_type: str, stack_depth=3) -> None:
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

    def has_record(self) -> bool:
        return not (self._data is None or self._packet is None or self._codec is None)

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        raise NotImplementedError()

    def encode_on(self, visitor: PacketVisitor) -> None:
        assert self.has_record()
        self.encode_children(visitor)
        data = self._codec.encode(self._packet)
        try:
            packet_str = self._get_packet_str(visitor)
            packet_info = '\n{}\n  {}'.format(self.called_line, packet_str)
            visitor.visit_encode_task(self._data, data, packet_info)
            self._log(packet_str)
        except AssertionError as e:
            self.encode_error_hook(visitor, e, data, self.called_line)

    def encode_children(self, visitor: PacketVisitor) -> None:
        pass

    def encode_error_hook(self, visitor: PacketVisitor, exc: AssertionError, data: bytes, called_line: str) -> None:
        raise exc

    def try_on_child(self, method: Callable[..., None], *args) -> Any:
        assert self.has_record()
        # noinspection PyUnresolvedReferences
        child = method.__self__
        packet_info = '  {} {}'.format(self._packet_type, self._packet)
        try:
            return method(*args)
        except _WrappedException as e:
            message = '{}\n'.format(e.args[0], packet_info)
            raise _WrappedException(e.exc, e.tb, message) from None
        except Exception as e:
            interrupt_for_pycharm(e, child.called_line, packet_info)
            message = '{} occurred while testing\n{}'.format(repr(e), child.called_line, packet_info)
            raise _WrappedException(e, sys.exc_info()[2], message) from None

    def _summarize_bytes(self, m: re.match) -> str:
        bytes_data = eval(m[1])  # type: bytes
        length = len(bytes_data)
        return repr(bytes_data) if length <= self._MAX_BYTES_LEN else '[{} bytes]'.format(length)

    def _get_packet_str(self, visitor: PacketVisitor) -> str:
        if visitor.is_enabled_bytes_mask():
            packet_str = str(self._packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
            packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(self._summarize_bytes, packet_str)
            packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(self._summarize_bytes, packet_str)
        else:
            packet_str = str(self._packet)
        return packet_str

    def _log(self, packet_str: str) -> None:
        _logger.info('%s\n  -> %s\n%s', packet_str, self._data.hex(), self.called_line)

    def print_packet(self, visitor: PacketVisitor) -> None:
        self._log(self._get_packet_str(visitor))


class GamePacket(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        """ Game packet analyzer."""
        super().__init__('Game packet')
        self._args = args
        self._kwargs = kwargs

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        packet = game_packet_codec.decode(data, context)
        visitor.visit_decode_game_packet_task(packet, data, context, *self._args, **self._kwargs)
        self.record_decoded(data[:context.length], packet, game_packet_codec)
        return context.length


class ConnectionPacket(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        """ Connection packet analyzer."""
        super().__init__('Connection packet')
        self._args = args
        self._kwargs = kwargs

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        packet = connection_packet_codec.decode(data, context)
        visitor.visit_decode_connection_packet_task(packet, data, context, *self._args, **self._kwargs)
        self.record_decoded(data[:context.length], packet, connection_packet_codec)
        return context.length


class Batch(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        """ Batch packet analyzer."""
        super().__init__('Batch packet')
        self._args = args
        self._kwargs = kwargs
        self._children = []
        if 'packet_id' not in self._kwargs:
            self._kwargs['packet_id'] = ConnectionPacketID.BATCH

    def that_has(self, *game_packet: GamePacket):
        self._children.extend(game_packet)
        return self

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        packet = connection_packet_codec.decode(data, context)
        visitor.visit_decode_batch_task(packet, data, context, len(self._children), *self._args, **self._kwargs)
        self.record_decoded(data[:context.length], packet, connection_packet_codec)
        for payload, child in zip(packet.payloads, self._children):
            self.try_on_child(child.decode_on, visitor, payload)
        return context.length

    def encode_children(self, visitor: PacketVisitor):
        for child in self._children:
            self.try_on_child(child.encode_on, visitor)

    def encode_error_hook(self, visitor: PacketVisitor, exc: AssertionError, data: bytes, called_line: str):
        print('Warning: There may be differences in compression results:\n', called_line, file=sys.stderr)
        self.decode_on(visitor, data)
        self.encode_on(visitor)

    def print_packet(self, visitor: PacketVisitor):
        for child in self._children:
            child.print_packet(visitor)
        super().print_packet(visitor)


class Capsule(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        """ Encapsulation of RakNet packet analyzer."""
        super().__init__('Encapsulation')
        self._args = args
        self._kwargs = kwargs
        self._child = None

    def that_has(self, packet: Union[ConnectionPacket, Batch]):
        self._child = packet
        return self

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        capsule = raknet_capsule_codec.decode(data, context)
        visitor.visit_decode_capsule_task(capsule, data, context, *self._args, **self._kwargs)
        self.record_decoded(data[:context.length], capsule, raknet_capsule_codec)
        if self._child is not None:
            self.try_on_child(self._child.decode_on, visitor, capsule.payload)
        return context.length

    def encode_children(self, visitor: PacketVisitor):
        if self._child is not None:
            self.try_on_child(self._child.encode_on, visitor)


class RakNetPacket(PacketAnalyzer):

    def __init__(self, *args, **kwargs):
        """ RakNet packet analyzer."""
        super().__init__('RakNet packet')
        self._args = args
        self._kwargs = kwargs
        self._children = []

    def that_has(self, *capsule: Capsule):
        self._children.extend(capsule)
        return self

    def _decode_raknet_packet(self, visitor: PacketVisitor, data: bytes):
        context = PacketCodecContext()
        packet = raknet_packet_codec.decode(data, context)
        visitor.visit_decode_raknet_packet_task(packet, data, context, *self._args, **self._kwargs)
        self.record_decoded(data, packet, raknet_packet_codec)
        return context.length, packet

    def _decode_raknet_encapsulation(self, visitor: PacketVisitor, packet: Packet):
        assert self.has_record()
        data = packet.payload
        payload_length = 0
        for analyzer in self._children:
            payload_length += self.try_on_child(analyzer.decode_on, visitor, data[payload_length:])
        visitor.visit_decode_capsules(data, payload_length)

    def decode_on(self, visitor: PacketVisitor, data: bytes):
        self._data = data
        try:
            length, packet = self._decode_raknet_packet(visitor, data)
            self._decode_raknet_encapsulation(visitor, packet)
            return length
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise _WrappedException(e.exc, e.tb, message) from None
        except Exception as e:
            interrupt_for_pycharm(e, self.called_line)
            message = '{} occurred while testing\n{}'.format(repr(e), self.called_line)
            raise _WrappedException(e, sys.exc_info()[2], message) from None

    def encode_children(self, visitor: PacketVisitor):
        for child in self._children:
            self.try_on_child(child.encode_on, visitor)


class EncodedData:

    def __init__(self, data: str):
        """ Encoded data validator.

        :param data: data that decode to packet
        """
        self._data = unhex(data)
        self._analyzer = None

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
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
        assertion = PacketAssertion(test_case)
        self._try_child_assertion(test_case, self._analyzer.decode_on, assertion, self._data)
        if and_verified_with_encoded_data:
            self._try_child_assertion(test_case, self._analyzer.encode_on, assertion)
        else:
            self._analyzer.print_packet(assertion)


class EncodedDataInFile(EncodedData):

    def __init__(self, test_case: CodecTestCase):
        """ Encoded data validator.

        Data is read from the file '{test_case_module_dir}/codec_data/{test_name}.txt'
        """
        with open(test_case.get_file_name('codec_data'), 'r') as file:
            data = ''.join(file.readlines())
        super().__init__(data)
