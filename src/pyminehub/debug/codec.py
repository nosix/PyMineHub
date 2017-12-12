"""
Debug tools for codec.

When debugging, execute `from pyminehub.debug.codec import *` in REPL.
"""
import re
import sys
import traceback
from typing import Callable, Union, Optional, Any

from pyminehub.mcpe.network.codec import connection_packet_codec
from pyminehub.mcpe.network.codec import game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketID
from pyminehub.network.codec import Codec
from pyminehub.network.codec import PacketCodecContext
from pyminehub.network.packet import Packet
from pyminehub.raknet.codec import capsule_codec as raknet_capsule_codec
from pyminehub.raknet.codec import raknet_packet_codec as raknet_packet_codec

_ASCII_CHARS = set(c for c in range(0x20, 0x7f))
_ASCII_CHARS_FOR_DOUBLE_QUOTE = _ASCII_CHARS - {0x22, 0x5c, 0x5d}  # " - \
_ASCII_CHARS_FOR_SINGLE_QUOTE = _ASCII_CHARS - {0x27, 0x5c, 0x5d}  # ' - \

_BYTES_REGEXP_FOR_DOUBLE_QUOTE = re.compile(
    r'(b"[{}\-\\\]]*?")'.format(''.join(chr(c) for c in _ASCII_CHARS_FOR_DOUBLE_QUOTE)))
_BYTES_REGEXP_FOR_SINGLE_QUOTE = re.compile(
    r"(b'[{}\-\\\]]*?')".format(''.join(chr(c) for c in _ASCII_CHARS_FOR_SINGLE_QUOTE)))


class PacketVisitor:

    def is_enabled_bytes_mask(self) -> bool:
        """If True, data beyond 16 bytes (MAX_BYTES_LEN of PacketAnalyzer) is summarized."""
        raise NotImplementedError()

    def get_log_function(self) -> Callable[..., None]:
        """Return log function object.

        If log output is unnecessary, it returns a function that does nothing.
        """
        raise NotImplementedError()

    def visit_decode_raknet_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        """It is called after decode on a RakNet packet."""
        raise NotImplementedError()

    def visit_decode_capsules(self, data: bytes, payload_length: int) -> None:
        """It is called after decoding capsules."""
        raise NotImplementedError()

    def visit_decode_capsule_task(
            self, capsule: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        """It is called after decode on a capsule."""
        raise NotImplementedError()

    def visit_decode_connection_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        """It is called after decode on a connection packet."""
        raise NotImplementedError()

    def visit_decode_batch_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext,
            expected_payloads_num: int, *args, **kwargs) -> None:
        """It is called after decode on a batch packet."""
        raise NotImplementedError()

    def visit_decode_game_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, *args, **kwargs) -> None:
        """It is called after decode on a game packet."""
        raise NotImplementedError()

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        """It is called after each packet is encoded."""
        raise NotImplementedError()

    def try_action(
            self, action_of_raising_exception: Callable[[], None],
            called_line: Optional[str]=None, message: Optional[str]=None) -> None:
        """Override when doing exception handling."""
        action_of_raising_exception()


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

    def record_decoded(self, data: bytes, packet: Packet, codec: Codec) -> None:
        """Record the decoded result."""
        self._data = data
        self._packet = packet
        self._codec = codec

    def has_record(self) -> bool:
        return not (self._data is None or self._packet is None or self._codec is None)

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        raise NotImplementedError()

    def encode_on(self, visitor: PacketVisitor) -> None:
        """Encode the decoded result."""
        assert self.has_record()
        self.encode_children(visitor)
        data = self._codec.encode(self._packet)
        try:
            packet_str = self._get_packet_str(visitor.is_enabled_bytes_mask())
            packet_info = '\n{}\n  {}'.format(self.called_line, packet_str)
            visitor.visit_encode_task(self._data, data, packet_info)
            self._log(visitor.get_log_function(), packet_str)
        except AssertionError as e:
            self.encode_error_hook(visitor, e, data, self.called_line)

    def encode_children(self, visitor: PacketVisitor) -> None:
        """Override if there are child elements."""
        pass

    def encode_error_hook(self, visitor: PacketVisitor, exc: AssertionError, data: bytes, called_line: str) -> None:
        """Overrides when there is processing at the time of exception occurrence."""
        raise exc

    def try_on_child(self, method: Callable[..., None], visitor: PacketVisitor, *args) -> Any:
        assert self.has_record()
        # noinspection PyUnresolvedReferences
        child = method.__self__
        packet_info = '  {} {}'.format(self._packet_type, self._packet)
        return visitor.try_action(lambda: method(visitor, *args), child.called_line, packet_info)

    def _summarize_bytes(self, m: re.match) -> str:
        bytes_data = eval(m[1])  # type: bytes
        length = len(bytes_data)
        return repr(bytes_data) if length <= self._MAX_BYTES_LEN else '[{} bytes]'.format(length)

    def _get_packet_str(self, is_enabled_bytes_mask: bool) -> str:
        if is_enabled_bytes_mask:
            packet_str = str(self._packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
            packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(self._summarize_bytes, packet_str)
            packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(self._summarize_bytes, packet_str)
        else:
            packet_str = str(self._packet)
        return packet_str

    def _log(self, log: Callable[..., None], packet_str: str) -> None:
        log('%s\n  -> %s\n%s', packet_str, self._data.hex(), self.called_line)

    def print_packet(self, visitor: PacketVisitor) -> None:
        self._log(visitor.get_log_function(), self._get_packet_str(visitor.is_enabled_bytes_mask()))


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

        def action():
            length, packet = self._decode_raknet_packet(visitor, data)
            self._decode_raknet_encapsulation(visitor, packet)
            return length
        visitor.try_action(action, self.called_line)

    def encode_children(self, visitor: PacketVisitor):
        for child in self._children:
            self.try_on_child(child.encode_on, visitor)
