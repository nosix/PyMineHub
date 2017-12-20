"""
Debug tools for codec.

When debugging, execute `from util.codec import *` in REPL.

>>> decode('840200000000480000000000003d3810')
[0] 840200000000480000000000003d3810
[1] CUSTOM_PACKET_4(id=132, packet_sequence_num=2, payload=b'\\x00\\x00H\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[2] UNRELIABLE(id=0, payload_length=72, payload=b'\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[3] CONNECTED_PING(id=0, ping_time_since_start=4012048)
"""
import re
import sys
import traceback
from binascii import unhexlify as unhex
from collections import defaultdict
from enum import Enum
from typing import *

from pyminehub.mcpe.network.codec import connection_packet_codec
from pyminehub.mcpe.network.codec import game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketType
from pyminehub.mcpe.network.packet import GamePacketType
from pyminehub.network.codec import Codec
from pyminehub.network.codec import PacketCodecContext
from pyminehub.raknet.codec import raknet_frame_codec
from pyminehub.raknet.codec import raknet_packet_codec
from pyminehub.raknet.fragment import MessageFragment
from pyminehub.raknet.frame import RakNetFrameType, RakNetFrame as _RakNetFrame
from pyminehub.raknet.packet import RakNetPacketType
from pyminehub.typevar import T
from pyminehub.value import ValueObject, ValueType
from util.exception import try_action

_ASCII_CHARS = set(c for c in range(0x20, 0x7f))
_ASCII_CHARS_FOR_DOUBLE_QUOTE = _ASCII_CHARS - {0x22, 0x5c, 0x5d}  # " - \
_ASCII_CHARS_FOR_SINGLE_QUOTE = _ASCII_CHARS - {0x27, 0x5c, 0x5d}  # ' - \

_BYTES_REGEXP_FOR_DOUBLE_QUOTE = re.compile(
    r'(b"[{}\-\\\]]*?")'.format(''.join(chr(c) for c in _ASCII_CHARS_FOR_DOUBLE_QUOTE)))
_BYTES_REGEXP_FOR_SINGLE_QUOTE = re.compile(
    r"(b'[{}\-\\\]]*?')".format(''.join(chr(c) for c in _ASCII_CHARS_FOR_SINGLE_QUOTE)))


def get_packet_str(packet: ValueObject, bytes_mask_threshold: Optional[int]=16) -> str:
    if bytes_mask_threshold is not None:
        def _summarize_bytes(m: re.match) -> str:
            bytes_data = eval(m[1])  # type: bytes
            length = len(bytes_data)
            return repr(bytes_data) if length <= bytes_mask_threshold else '[{} bytes]'.format(length)

        packet_str = str(packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
        packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(_summarize_bytes, packet_str)
        packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(_summarize_bytes, packet_str)
    else:
        packet_str = str(packet)
    return packet_str


class AnalyzingContext:

    def __init__(self) -> None:
        self._fragment = defaultdict(MessageFragment)  # type: Dict[str, MessageFragment]
        self._values = {}

    def get_bytes_mask_threshold(self) -> Optional[int]:
        """Bytes data is summarized when data length greater than threshold."""
        return 16

    def get_log_function(self) -> Callable[..., None]:
        """Return log function object.

        If log output is unnecessary, it returns a function that does nothing.
        """
        return lambda *args: None

    def assert_equal(self, expected: T, actual: T, message: str= '') -> None:
        assert expected == actual, message if message is not None else ''

    def append_fragment(self, key: str, frame: _RakNetFrame) -> Optional[bytes]:
        self._fragment[key].append(
            frame.split_packet_id, frame.split_packet_count, frame.split_packet_index, frame.payload)
        return self._fragment[key].pop(frame.split_packet_id)

    def __repr__(self) -> str:
        return repr(self._values)

    def __setitem__(self, key, value) -> None:
        self._values[key] = value

    def __getitem__(self, key) -> T:
        return self._values[key]

    def update(self, values: dict) -> None:
        self._values.update(values)


class AnalyzingVisitor:

    def get_context(self) -> AnalyzingContext:
        raise NotImplementedError()

    def append_fragment(self, frame: _RakNetFrame) -> Optional[bytes]:
        return self.get_context().append_fragment('default', frame)

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        self.get_context().assert_equal(expected, actual, message)

    def assert_equal_for_encoding(self, expected: T, actual: T, message: str= '') -> None:
        self.get_context().assert_equal(expected, actual, message)

    def visit_after_decoding(
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs
    ) -> ValueObject:
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

    def visit_after_encoding(self, packet: ValueObject, data: bytes, packet_str: str, called: str) -> None:
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


_PAT = TypeVar('PAT', bound='PacketAnalyzer')


class PacketAnalyzer:

    def __init__(self, packet_id: ValueType, codec: Codec, stack_depth=3) -> None:
        self._called_line = self._mask_path(traceback.format_stack()[-stack_depth])
        self._packet_type = self.__class__.__name__
        self._packet_id = packet_id
        self._label = ''
        self._codec = codec
        self._data = None
        self._packet = None

    @staticmethod
    def _mask_path(called_line: str) -> str:
        m = re.search(r'File "(.+)/.+\.py"', called_line)
        return called_line.replace(m[1], '.', 1)

    def get_called_line(self) -> str:
        return '{}\n{}'.format(self._label, self._called_line)

    def with_label(self, label: str):
        self._label = label
        for child in self.get_child_analyzers():
            child.with_label(label)
        return self

    def get_extra_kwargs(self) -> dict:
        """Return values that is passed visit_after_decoding in visitor."""
        return {}

    def get_child_analyzers(self) -> Iterator[_PAT]:
        return iter([])

    def get_child_targets(
            self, visitor: AnalyzingVisitor, packet: Optional[ValueObject]=None
    ) -> Iterator[Tuple[bytes, _PAT]]:
        """Get pairs that has packet payload and child PacketAnalyzer.

        :param visitor: AnalyzingVisitor object
        :param packet: packet payload is gotten from this packet
        :return: pairs that has packet payload and child PacketAnalyzer
        """
        return iter([])

    def get_payload_attr(self, payloads: Tuple[bytes, ...]) -> Dict[str, Any]:
        """Return pair of attribute name and attribute value.

        :param payloads: used in attribute value
        :return: for example, {'payload': b'[some bytes]', 'payload_length': 128}
        """
        return {}

    def does_assert_data_length(self) -> bool:
        """Return True if PacketAnalyzer asserts equal length of data after decoding."""
        return True

    def does_retry_encoding(self) -> bool:
        """Return True if AacketAnalyzer retry encoding when encoding result does not match original encoded data.

        When retrying, the encoded data is decoded and the decoded data is re-encoded.
        """
        return False

    def _record_decoded(self, data: bytes, packet: ValueObject) -> None:
        """Record the decoded result."""
        self._data = data
        self._packet = packet

    def has_record(self) -> bool:
        """Has the decoded result."""
        return not (self._data is None or self._packet is None)

    def decode_on(self, visitor: AnalyzingVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        packet = self._codec.decode(data, context)
        packet_str = get_packet_str(packet, visitor.get_context().get_bytes_mask_threshold())
        visitor.assert_equal_for_decoding(
            self._packet_id, type(self._packet_id)(packet.id), str(packet))
        if self.does_assert_data_length():
            visitor.assert_equal_for_decoding(len(data), context.length)
        if hasattr(packet, 'payloads'):
            visitor.assert_equal_for_decoding(len(list(self.get_child_targets(visitor))), len(packet.payloads))
        packet = visitor.visit_after_decoding(
            data, self._packet_id, packet, packet_str, self.get_called_line(), **self.get_extra_kwargs())
        self._record_decoded(data[:context.length], packet)
        for payload, child in self.get_child_targets(visitor, packet):
            # noinspection PyTypeChecker
            self.try_on_child(child.decode_on, visitor, payload)
        return context.length

    def encode_on(self, visitor: AnalyzingVisitor, label: _Label=_Label.NONE) -> bytes:
        """Encode the decoded result to bytes data.

        :return: encoded bytes data
        """
        assert self.has_record()
        payloads = tuple(self._encode_children(visitor, label))
        # noinspection PyProtectedMember
        packet = self._packet._replace(**self.get_payload_attr(payloads))
        data = self._codec.encode(packet)
        try:
            packet_str = get_packet_str(packet, visitor.get_context().get_bytes_mask_threshold())
            packet_info = '\n{}\n  {}'.format(self.get_called_line(), packet_str)
            visitor.assert_equal_for_encoding(self._data.hex(), data.hex(), packet_info)
            visitor.visit_after_encoding(packet, data, packet_str, self.get_called_line())
            self._log(visitor.get_context().get_log_function(), label, packet_str)
            return data
        except AssertionError as e:
            return self._retry_encoding(visitor, e, data, self.get_called_line())

    def _encode_children(self, visitor: AnalyzingVisitor, label: _Label) -> Generator[bytes, None, None]:
        """Override if there are child elements."""
        for _, child in self.get_child_targets(visitor):
            # noinspection PyUnresolvedReferences
            yield self.try_on_child(child.encode_on, visitor, label if label is _Label.NONE else _Label.HIDE)

    def _retry_encoding(
            self, visitor: AnalyzingVisitor, exc: AssertionError, data: bytes, called_line: str) -> ValueObject:
        """Overrides when there is processing at the time of exception occurrence."""
        if self.does_retry_encoding():
            print('Warning: There may be differences in compression results:\n', called_line, file=sys.stderr)
            self.decode_on(visitor, data)
            return self.encode_on(visitor, _Label.WARNING)
        else:
            raise exc

    def try_on_child(self, method: Callable[..., None], visitor: AnalyzingVisitor, *args) -> Any:
        assert self.has_record()
        # noinspection PyUnresolvedReferences
        child = method.__self__
        packet_info = '  {} {}'.format(self._packet_type, self._packet)
        return try_action(lambda: method(visitor, *args), child.get_called_line(), packet_info)

    def _log(self, log: Callable[..., None], label: _Label, packet_str: str) -> None:
        if label is not _Label.HIDE:
            title = '' if label is _Label.NONE else label.name + ':'
            log('%s%s\n  -> %s\n%s', title, packet_str, self._data.hex(), self.get_called_line())

    def print_packet(self, visitor: AnalyzingVisitor) -> None:
        self._log(visitor.get_context().get_log_function(),
                  _Label.NONE,
                  get_packet_str(self._packet, visitor.get_context().get_bytes_mask_threshold()))


class GamePacket(PacketAnalyzer):

    def __init__(self, packet_id: GamePacketType, *args, **kwargs) -> None:
        super().__init__(packet_id, game_packet_codec)
        self._args = args
        self._kwargs = kwargs

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs


class ConnectionPacket(PacketAnalyzer):

    def __init__(self, packet_id: ConnectionPacketType, *args, **kwargs) -> None:
        super().__init__(packet_id, connection_packet_codec)
        self._args = args
        self._kwargs = kwargs

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs


class Batch(PacketAnalyzer):

    def __init__(self) -> None:
        super().__init__(ConnectionPacketType.BATCH, connection_packet_codec)
        self._children = []

    def that_has(self, *game_packet: GamePacket):
        self._children.extend(game_packet)
        return self

    def get_child_analyzers(self) -> Iterator[PacketAnalyzer]:
        return iter(self._children)

    def get_child_targets(
            self, visitor: AnalyzingVisitor, packet: Optional[ValueObject]=None
    ) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is not None:
            return zip(packet.payloads, self._children)
        else:
            return iter((b'', child) for child in self._children)

    def get_payload_attr(self, payloads: Tuple[bytes, ...]) -> Dict[str, Tuple[bytes, ...]]:
        return {'payloads': payloads}

    def does_retry_encoding(self) -> bool:
        return True

    def print_packet(self, visitor: AnalyzingVisitor) -> None:
        for child in self._children:
            child.print_packet(visitor)
        super().print_packet(visitor)


class RakNetFrame(PacketAnalyzer):

    def __init__(self, packet_id: RakNetFrameType, *args, **kwargs) -> None:
        super().__init__(packet_id, raknet_frame_codec)
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

    def get_child_analyzers(self) -> Iterator[PacketAnalyzer]:
        return iter([]) if self._child is None else iter([self._child])

    def get_child_targets(
            self, visitor: AnalyzingVisitor, packet: Optional[ValueObject]=None
    ) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is None:
            return iter([(b'', self._child)])
        payload = packet.payload
        if RakNetFrameType(packet.id) == RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT:
            payload = visitor.append_fragment(packet)
        return iter([]) if self._child is None else \
            iter([(b'', self._child)]) if payload is None else \
            iter([(payload, self._child)])

    def get_payload_attr(self, payloads: Tuple[bytes, ...]) -> Dict[str, bytes]:
        assert len(payloads) == 1
        return {'payload': payloads[0], 'payload_length': len(payloads[0] * 8)}  # unit of payload_length is bits

    def does_retry_encoding(self) -> bool:
        return True

    def does_assert_data_length(self) -> bool:
        return False


class RakNetPacket(PacketAnalyzer):

    def __init__(self, packet_id: RakNetPacketType, *args, **kwargs) -> None:
        super().__init__(packet_id, raknet_packet_codec)
        self._args = args
        self._kwargs = kwargs
        self._children = []

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs

    def that_has(self, *frame: RakNetFrame):
        self._children.extend(frame)
        return self

    def get_child_analyzers(self) -> Iterator[PacketAnalyzer]:
        return iter(self._children)

    def get_child_targets(
            self, visitor: AnalyzingVisitor, packet: Optional[ValueObject]=None
    ) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is not None:
            return iter([])  # use _decode_raknet_frame
        else:
            return iter((b'', child) for child in self._children)

    def _decode_raknet_packet(self, visitor: AnalyzingVisitor, data: bytes) -> None:
        super().decode_on(visitor, data)

    def _decode_raknet_frame(self, visitor: AnalyzingVisitor) -> None:
        assert self.has_record()
        data = self._packet.payload
        payload_length = 0
        for analyzer in self._children:
            payload_length += self.try_on_child(analyzer.decode_on, visitor, data[payload_length:])
        visitor.assert_equal_for_decoding(
            len(data), payload_length, 'RakNetPacket payload may be missing, the payload is "{}"'.format(data.hex()))

    def decode_on(self, visitor: AnalyzingVisitor, data: bytes) -> None:
        def action():
            self._decode_raknet_packet(visitor, data)
            if len(self._children) > 0:
                self._decode_raknet_frame(visitor)
        try_action(action, self.get_called_line())

    def get_payload_attr(self, payloads: Tuple[bytes, ...]) -> Dict[str, bytes]:
        return {'payload': b''.join(payloads)}

    def does_retry_encoding(self) -> bool:
        return True


class DecodeAgent:

    def __init__(self) -> None:
        self._fragment = MessageFragment()
        self._data = []
        self._packet = []
        self._decode_func = [
            self._decode_raknet_packet,
            self._decode_raknet_frame,
            self._decode_connection_packet,
            self._decode_game_packet]

    def __repr__(self) -> str:
        items = list(self._data)
        items.extend(get_packet_str(p) for p in self._packet)
        return '\n'.join('[{}] {}'.format(i, item) for i, item in enumerate(items))

    def __getitem__(self, index: int) -> ValueObject:
        if index < len(self._data):
            return self._data[index]
        else:
            return self._packet[index - len(self._data)]

    def clear(self):
        self.__init__()
        return self

    def _decode_raknet_packet(self, data: bytearray) -> None:
        context = PacketCodecContext()
        packet = raknet_packet_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payload'):
            data = bytearray(packet.payload)
            while len(data) > 0:
                self._decode_raknet_frame(data)

    def _decode_raknet_frame(self, data: bytearray) -> None:
        context = PacketCodecContext()
        packet = raknet_frame_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]

        if RakNetFrameType(packet.id) == RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT:
            self._fragment.append(
                packet.split_packet_id, packet.split_packet_count, packet.split_packet_index, packet.payload)
            payload = self._fragment.pop(packet.split_packet_id)
        else:
            payload = packet.payload

        if payload is not None:
            data = bytearray(payload)
            self._decode_connection_packet(data)
        else:
            print('FRAGMENT APPENDED')

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

    def decode(self, data: str, depth: int=0):
        self._data.append(data)
        data = bytearray(unhex(data))
        self._decode_func[depth](data)
        if len(data) > 0:
            print(data.hex())
        return self


agent = DecodeAgent()


def decode(data: str, depth: int=0) -> DecodeAgent:
    return agent.decode(data, depth)


def clear() -> DecodeAgent:
    return agent.clear()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
