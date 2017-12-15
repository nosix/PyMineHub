"""
Debug tools for codec.

When debugging, execute `from util.codec import *` in REPL.

decode('840200000000480000000000003d3810')
[0] 840200000000480000000000003d3810
[1] CUSTOM_PACKET_4(id=132, packet_sequence_num=2, payload=b'\x00\x00H\x00\x00\x00\x00\x00\x00=8\x10')
[2] UNRELIABLE(id=0, payload_length=72, payload=b'\x00\x00\x00\x00\x00\x00=8\x10')
[3] CONNECTED_PING(id=0, ping_time_since_start=4012048)
"""
import re
import sys
import traceback
from binascii import unhexlify as unhex
from enum import Enum
from typing import *

from pyminehub.mcpe.network.codec import connection_packet_codec
from pyminehub.mcpe.network.codec import game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketID
from pyminehub.mcpe.network.packet import GamePacketID
from pyminehub.network.codec import Codec
from pyminehub.network.codec import PacketCodecContext
from pyminehub.network.packet import Packet, PacketID
from pyminehub.raknet.codec import capsule_codec as raknet_capsule_codec
from pyminehub.raknet.codec import raknet_packet_codec as raknet_packet_codec
from pyminehub.raknet.encapsulation import CapsuleID
from pyminehub.raknet.packet import RakNetPacketID
from pyminehub.typing import T
from util.exception import try_action

_ASCII_CHARS = set(c for c in range(0x20, 0x7f))
_ASCII_CHARS_FOR_DOUBLE_QUOTE = _ASCII_CHARS - {0x22, 0x5c, 0x5d}  # " - \
_ASCII_CHARS_FOR_SINGLE_QUOTE = _ASCII_CHARS - {0x27, 0x5c, 0x5d}  # ' - \

_BYTES_REGEXP_FOR_DOUBLE_QUOTE = re.compile(
    r'(b"[{}\-\\\]]*?")'.format(''.join(chr(c) for c in _ASCII_CHARS_FOR_DOUBLE_QUOTE)))
_BYTES_REGEXP_FOR_SINGLE_QUOTE = re.compile(
    r"(b'[{}\-\\\]]*?')".format(''.join(chr(c) for c in _ASCII_CHARS_FOR_SINGLE_QUOTE)))


def get_packet_str(packet: Packet, bytes_mask_threshold: Optional[int]=16) -> str:
    if bytes_mask_threshold is not None:
        def _summarize_bytes(m: re.match) -> str:
            bytes_data = eval(m[1])  # type: bytes
            length = len(bytes_data)
            return repr(bytes_data) if length <= bytes_mask_threshold else '[{} bytes]'.format(length)

        packet_str = str(packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
        packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(_summarize_bytes, packet_str)
        packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(_summarize_bytes, packet_str)
    else:
        packet_str = str(packet)
    return packet_str


class PacketVisitor:

    def get_bytes_mask_threshold(self) -> Optional[int]:
        """Bytes data is summarized when data length greater than threshold."""
        return 16

    def get_log_function(self) -> Callable[..., None]:
        """Return log function object.

        If log output is unnecessary, it returns a function that does nothing.
        """
        return lambda *args: None

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        assert expected == actual, message if message is not None else ''

    def assert_equal_for_encoding(self, expected: T, actual: T, message: str= '') -> None:
        assert expected == actual, message if message is not None else ''

    def visit_after_decoding(
            self, data: bytes, packet_id: PacketID, packet: Packet, packet_str: str, called: str, **kwargs) -> Packet:
        """It is called after each packet is decodec.

        :param data: decoded data
        :param packet_id: packet ID specified by PacketAnalyzer constructor argument
        :param packet: decoding result packet
        :param packet_str: information of the packet
            Example:
                File "./codec_login_logout.py", line 12, in test_login_logout_c00
                  ConnectionPacket(ConnectionPacketID.CONNECTION_REQUEST)

                CONNECTION_REQUEST(id=9, client_guid=9700202662021728174, client_time_since_start=4012035, ...
        :param called: line number that constructor of PacketAnalyzer is called in
        :param kwargs: return value that is gotten from get_extra_kwargs method in PacketAnalyzer
        :return: updated decoding result packet
        """
        return packet

    def visit_after_encoding(self, packet: Packet, data: bytes, packet_str: str, called: str) -> None:
        """It is called after each packet is encoded.

        :param packet: encoded packet
        :param data: data that is encoded from the packet
        :param packet_str: information of the packet
            Example:
                File "./codec_login_logout.py", line 12, in test_login_logout_c00
                  ConnectionPacket(ConnectionPacketID.CONNECTION_REQUEST)

                CONNECTION_REQUEST(id=9, client_guid=9700202662021728174, client_time_since_start=4012035, ...
        :param called: line number that constructor of PacketAnalyzer is called in
        """
        pass


class _Label(Enum):
    NONE = 0
    HIDE = 1
    WARNING = 2


class PacketAnalyzer:

    def __init__(self, packet_id: PacketID, codec: Codec, stack_depth=3) -> None:
        called_line = traceback.format_stack()[-stack_depth]
        m = re.search(r'File "(.+)/.+\.py"', called_line)
        self.called_line = called_line.replace(m[1], '.', 1)
        self._packet_type = self.__class__.__name__
        self._packet_id = packet_id
        self._codec = codec
        self._data = None
        self._packet = None

    def get_extra_kwargs(self) -> dict:
        return {}

    def get_children(self, packet: Optional[Packet]=None) -> Iterator[Tuple[bytes, T]]:
        """Get pairs that has packet payload and child PacketAnalyzer.

        :param packet: packet payload is gotten from this packet
        :return: pairs that has packet payload and child PacketAnalyzer
        """
        return iter([])

    def get_payload_dict(self, payloads: Tuple[bytes, ...]) -> Dict[str, T]:
        return {}

    def does_assert_data_length(self) -> bool:
        """Return True if PacketAnalyzer asserts equal length of data after decoding."""
        return True

    def does_retry_encoding(self) -> bool:
        """Return True if AacketAnalyzer retry encoding when encoding result does not match original encoded data.

        When retrying, the encoded data is decoded and the decoded data is re-encoded.
        """
        return False

    def _record_decoded(self, data: bytes, packet: Packet) -> None:
        """Record the decoded result."""
        self._data = data
        self._packet = packet

    def has_record(self) -> bool:
        """Has the decoded result."""
        return not (self._data is None or self._packet is None)

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        packet = self._codec.decode(data, context)
        packet_str = get_packet_str(packet, visitor.get_bytes_mask_threshold())
        visitor.assert_equal_for_decoding(self._packet_id, type(self._packet_id)(packet.id), str(packet))
        if self.does_assert_data_length():
            visitor.assert_equal_for_decoding(len(data), context.length)
        if hasattr(packet, 'payloads'):
            visitor.assert_equal_for_decoding(len(list(self.get_children())), len(packet.payloads))
        packet = visitor.visit_after_decoding(
            data, self._packet_id, packet, packet_str, self.called_line, **self.get_extra_kwargs())
        self._record_decoded(data[:context.length], packet)
        for payload, child in self.get_children(packet):
            # noinspection PyTypeChecker
            self.try_on_child(child.decode_on, visitor, payload)
        return context.length

    def encode_on(self, visitor: PacketVisitor, label: _Label=_Label.NONE) -> bytes:
        """Encode the decoded result to bytes data.

        :return: encoded bytes data
        """
        assert self.has_record()
        payloads = tuple(self._encode_children(visitor, label))
        # noinspection PyProtectedMember
        packet = self._packet._replace(**self.get_payload_dict(payloads))
        data = self._codec.encode(packet)
        try:
            packet_str = get_packet_str(packet, visitor.get_bytes_mask_threshold())
            packet_info = '\n{}\n  {}'.format(self.called_line, packet_str)
            visitor.assert_equal_for_encoding(self._data.hex(), data.hex(), packet_info)
            visitor.visit_after_encoding(packet, data, packet_str, self.called_line)
            self._log(visitor.get_log_function(), label, packet_str)
            return data
        except AssertionError as e:
            return self._retry_encoding(visitor, e, data, self.called_line)

    def _encode_children(self, visitor: PacketVisitor, label: _Label) -> Generator[bytes, None, None]:
        """Override if there are child elements."""
        for _, child in self.get_children():
            # noinspection PyUnresolvedReferences
            yield self.try_on_child(child.encode_on, visitor, label if label is _Label.NONE else _Label.HIDE)

    def _retry_encoding(self, visitor: PacketVisitor, exc: AssertionError, data: bytes, called_line: str) -> Packet:
        """Overrides when there is processing at the time of exception occurrence."""
        if self.does_retry_encoding():
            print('Warning: There may be differences in compression results:\n', called_line, file=sys.stderr)
            self.decode_on(visitor, data)
            return self.encode_on(visitor, _Label.WARNING)
        else:
            raise exc

    def try_on_child(self, method: Callable[..., None], visitor: PacketVisitor, *args) -> Any:
        assert self.has_record()
        # noinspection PyUnresolvedReferences
        child = method.__self__
        packet_info = '  {} {}'.format(self._packet_type, self._packet)
        return try_action(lambda: method(visitor, *args), child.called_line, packet_info)

    def _log(self, log: Callable[..., None], label: _Label, packet_str: str) -> None:
        if label is not _Label.HIDE:
            title = '' if label is _Label.NONE else label.name + ':'
            log('%s%s\n  -> %s\n%s', title, packet_str, self._data.hex(), self.called_line)

    def print_packet(self, visitor: PacketVisitor) -> None:
        self._log(visitor.get_log_function(),
                  _Label.NONE,
                  get_packet_str(self._packet, visitor.get_bytes_mask_threshold()))


class GamePacket(PacketAnalyzer):

    def __init__(self, packet_id: GamePacketID, *args, **kwargs) -> None:
        super().__init__(packet_id, game_packet_codec)
        self._args = args
        self._kwargs = kwargs

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs


class ConnectionPacket(PacketAnalyzer):

    def __init__(self, packet_id: ConnectionPacketID, *args, **kwargs) -> None:
        super().__init__(packet_id, connection_packet_codec)
        self._args = args
        self._kwargs = kwargs

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs


class Batch(PacketAnalyzer):

    def __init__(self) -> None:
        super().__init__(ConnectionPacketID.BATCH, connection_packet_codec)
        self._children = []

    def that_has(self, *game_packet: GamePacket):
        self._children.extend(game_packet)
        return self

    def get_children(self, packet: Optional[Packet]=None) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is not None:
            return zip(packet.payloads, self._children)
        else:
            return iter((b'', child) for child in self._children)

    def get_payload_dict(self, payloads: Tuple[bytes, ...]) -> Dict[str, Tuple[bytes, ...]]:
        return {'payloads': payloads}

    def does_retry_encoding(self) -> bool:
        return True

    def print_packet(self, visitor: PacketVisitor) -> None:
        for child in self._children:
            child.print_packet(visitor)
        super().print_packet(visitor)


class Capsule(PacketAnalyzer):

    def __init__(self, packet_id: CapsuleID, *args, **kwargs) -> None:
        super().__init__(packet_id, raknet_capsule_codec)
        self._args = args
        self._kwargs = kwargs
        self._child = None

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs

    def that_has(self, packet: Union[ConnectionPacket, Batch]):
        self._child = packet
        return self

    def get_children(self, packet: Optional[Packet]=None) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is not None:
            return iter([(packet.payload, self._child)])
        else:
            return iter([(b'', self._child)])

    def get_payload_dict(self, payloads: Tuple[bytes, ...]) -> Dict[str, bytes]:
        assert len(payloads) == 1
        return {'payload': payloads[0], 'payload_length': len(payloads[0] * 8)}  # unit of payload_length is bits

    def does_retry_encoding(self) -> bool:
        return True

    def does_assert_data_length(self) -> bool:
        return False


class RakNetPacket(PacketAnalyzer):

    def __init__(self, packet_id: RakNetPacketID, *args, **kwargs) -> None:
        super().__init__(packet_id, raknet_packet_codec)
        self._args = args
        self._kwargs = kwargs
        self._children = []

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs

    def that_has(self, *capsule: Capsule):
        self._children.extend(capsule)
        return self

    def get_children(self, packet: Optional[Packet]=None) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is not None:
            return iter([])  # use _decode_raknet_encapsulation
        else:
            return iter((b'', child) for child in self._children)

    def _decode_raknet_packet(self, visitor: PacketVisitor, data: bytes) -> None:
        super().decode_on(visitor, data)

    def _decode_raknet_encapsulation(self, visitor: PacketVisitor) -> None:
        assert self.has_record()
        data = self._packet.payload
        payload_length = 0
        for analyzer in self._children:
            payload_length += self.try_on_child(analyzer.decode_on, visitor, data[payload_length:])
        visitor.assert_equal_for_decoding(
            len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> None:
        def action():
            self._decode_raknet_packet(visitor, data)
            if len(self._children) > 0:
                self._decode_raknet_encapsulation(visitor)
        try_action(action, self.called_line)

    def get_payload_dict(self, payloads: Tuple[bytes, ...]) -> Dict[str, bytes]:
        return {'payload': b''.join(payloads)}

    def does_retry_encoding(self) -> bool:
        return True


class DecodeAgent:

    def __init__(self) -> None:
        self._data = None
        self._packet = []

    def __repr__(self) -> str:
        items = [self._data]
        items.extend(get_packet_str(p) for p in self._packet)
        return '\n'.join('[{}] {}'.format(i, item) for i, item in enumerate(items))

    def __getitem__(self, index: int) -> Packet:
        if index == 0:
            return self._data
        else:
            return self._packet[index - 1]

    def _decode_raknet_packet(self, data: bytearray) -> None:
        context = PacketCodecContext()
        packet = raknet_packet_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payload'):
            data = bytearray(packet.payload)
            while len(data) > 0:
                self._decode_raknet_capsule(data)

    def _decode_raknet_capsule(self, data: bytearray) -> None:
        context = PacketCodecContext()
        packet = raknet_capsule_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]
        data = bytearray(packet.payload)
        self._decode_connection_packet(data)

    def _decode_connection_packet(self, data: bytearray) -> None:
        context = PacketCodecContext()
        packet = connection_packet_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payloads'):
            for payload in packet.payloads:
                data = bytearray(payload)
                self._decode_game_packet(data)

    def _decode_game_packet(self, data: bytearray) -> None:
        context = PacketCodecContext()
        packet = game_packet_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]

    def decode(self, data: str):
        self._data = data
        data = bytearray(unhex(data))
        self._decode_raknet_packet(data)
        if len(data) > 0:
            print(data.hex())
        return self


def decode(data: str) -> DecodeAgent:
    return DecodeAgent().decode(data)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
