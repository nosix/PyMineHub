"""
Debug tools for codec.

When debugging, execute `from pyminehub.debug.codec import *` in REPL.
"""
import re
import sys
import traceback
from typing import Iterator, Tuple, Callable, Union, Optional, Any

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

_ASCII_CHARS = set(c for c in range(0x20, 0x7f))
_ASCII_CHARS_FOR_DOUBLE_QUOTE = _ASCII_CHARS - {0x22, 0x5c, 0x5d}  # " - \
_ASCII_CHARS_FOR_SINGLE_QUOTE = _ASCII_CHARS - {0x27, 0x5c, 0x5d}  # ' - \

_BYTES_REGEXP_FOR_DOUBLE_QUOTE = re.compile(
    r'(b"[{}\-\\\]]*?")'.format(''.join(chr(c) for c in _ASCII_CHARS_FOR_DOUBLE_QUOTE)))
_BYTES_REGEXP_FOR_SINGLE_QUOTE = re.compile(
    r"(b'[{}\-\\\]]*?')".format(''.join(chr(c) for c in _ASCII_CHARS_FOR_SINGLE_QUOTE)))


class PacketVisitor:

    def get_bytes_mask_threshold(self) -> Optional[int]:
        """Bytes data is summarized when data length greater than threshold."""
        return 16

    def get_log_function(self) -> Callable[..., None]:
        """Return log function object.

        If log output is unnecessary, it returns a function that does nothing.
        """
        return lambda *args: None

    def visit_decode_capsules(self, data: bytes, decoded_payload_length: int) -> None:
        """It is called after decoding capsules.

        :param data: decoded data
        :param decoded_payload_length: decoded payload length in data
        """
        raise NotImplementedError()

    def visit_decode_task(
            self, packet_id_cls: PacketID, packet: Packet, data: bytes,
            context: PacketCodecContext, *args, **kwargs) -> None:
        """It is called after each packet is decodec.
        
        :param packet_id_cls: it represents the type of decoded packet
        :param packet: decoding result packet
        :param data: decoded data
        :param context: context at the end of decoding
        :param args: return value that is gotten from get_extra_args method in PacketAnalyzer
        :param kwargs: return value that is gotten from get_extra_kwargs method in PacketAnalyzer
        """
        raise NotImplementedError()

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        """It is called after each packet is encoded.

        :param original_data: data that is decoded to the packet
        :param encoded_data: data that is encoded from the packet
        :param packet_info: information of the packet
            Example:
                File "./codec_login_logout.py", line 12, in test_login_logout_c00
                  ConnectionPacket(ConnectionPacketID.CONNECTION_REQUEST)

                CONNECTION_REQUEST(id=9, client_guid=9700202662021728174, client_time_since_start=4012035, ...
        """
        raise NotImplementedError()

    def try_action(
            self, action_of_raising_exception: Callable[[], None],
            called_line: Optional[str]=None, packet_info: Optional[str]=None) -> None:
        """Override when doing exception handling.

        :param action_of_raising_exception: you need to call this function
        :param called_line: line where PacketAnalyzer's constructor is called
        :param packet_info: information of the packet
            Example:
                Batch BATCH(id=254, payloads=(bytearray(b'4\x00\x00\xfd\x07\x02\x06\x06\n\x82\xfc...
        """
        action_of_raising_exception()


class PacketAnalyzer:

    def __init__(self, packet_id_cls: PacketID, codec: Codec, stack_depth=3) -> None:
        called_line = traceback.format_stack()[-stack_depth]
        m = re.search(r'File "(.+)/.+\.py"', called_line)
        self.called_line = called_line.replace(m[1], '.', 1)
        self._packet_type = self.__class__.__name__
        self._packet_id_cls = packet_id_cls
        self._codec = codec
        self._data = None
        self._packet = None

    def get_extra_args(self) -> tuple:
        return ()

    def get_extra_kwargs(self) -> dict:
        return {}

    def get_children(self, packet: Optional[Packet]=None) -> Iterator[Tuple[bytes, T]]:
        return iter([])

    def _record_decoded(self, data: bytes, packet: Packet) -> None:
        """Record the decoded result."""
        self._data = data
        self._packet = packet

    def has_record(self) -> bool:
        return not (self._data is None or self._packet is None)

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> int:
        context = PacketCodecContext()
        packet = self._codec.decode(data, context)
        visitor.visit_decode_task(
            self._packet_id_cls, packet, data, context, *self.get_extra_args(), **self.get_extra_kwargs())
        self._record_decoded(data[:context.length], packet)
        for payload, child in self.get_children(packet):
            # noinspection PyTypeChecker
            self.try_on_child(child.decode_on, visitor, payload)
        return context.length

    def encode_on(self, visitor: PacketVisitor) -> None:
        """Encode the decoded result."""
        assert self.has_record()
        self._encode_children(visitor)
        data = self._codec.encode(self._packet)
        try:
            packet_str = self._get_packet_str(visitor.get_bytes_mask_threshold())
            packet_info = '\n{}\n  {}'.format(self.called_line, packet_str)
            visitor.visit_encode_task(self._data, data, packet_info)
            self._log(visitor.get_log_function(), packet_str)
        except AssertionError as e:
            self.encode_error_hook(visitor, e, data, self.called_line)

    def _encode_children(self, visitor: PacketVisitor) -> None:
        """Override if there are child elements."""
        for _, child in self.get_children():
            # noinspection PyUnresolvedReferences
            self.try_on_child(child.encode_on, visitor)

    def encode_error_hook(self, visitor: PacketVisitor, exc: AssertionError, data: bytes, called_line: str) -> None:
        """Overrides when there is processing at the time of exception occurrence."""
        raise exc

    def try_on_child(self, method: Callable[..., None], visitor: PacketVisitor, *args) -> Any:
        assert self.has_record()
        # noinspection PyUnresolvedReferences
        child = method.__self__
        packet_info = '  {} {}'.format(self._packet_type, self._packet)
        return visitor.try_action(lambda: method(visitor, *args), child.called_line, packet_info)

    def _get_packet_str(self, bytes_mask_threshold: Optional[int]) -> str:
        if bytes_mask_threshold is not None:
            def _summarize_bytes(m: re.match) -> str:
                bytes_data = eval(m[1])  # type: bytes
                length = len(bytes_data)
                return repr(bytes_data) if length <= bytes_mask_threshold else '[{} bytes]'.format(length)

            packet_str = str(self._packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
            packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(_summarize_bytes, packet_str)
            packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(_summarize_bytes, packet_str)
        else:
            packet_str = str(self._packet)
        return packet_str

    def _log(self, log: Callable[..., None], packet_str: str) -> None:
        log('%s\n  -> %s\n%s', packet_str, self._data.hex(), self.called_line)

    def print_packet(self, visitor: PacketVisitor) -> None:
        self._log(visitor.get_log_function(), self._get_packet_str(visitor.get_bytes_mask_threshold()))


class GamePacket(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(GamePacketID, game_packet_codec)
        self._args = args
        self._kwargs = kwargs

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs


class ConnectionPacket(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(ConnectionPacketID, connection_packet_codec)
        self._args = args
        self._kwargs = kwargs

    def get_extra_args(self) -> tuple:
        return self._args

    def get_extra_kwargs(self) -> dict:
        return self._kwargs


class Batch(PacketAnalyzer):

    def __init__(self) -> None:
        super().__init__(ConnectionPacketID, connection_packet_codec)
        self._children = []

    def get_extra_args(self) -> tuple:
        return ConnectionPacketID.BATCH, len(self._children)

    def that_has(self, *game_packet: GamePacket):
        self._children.extend(game_packet)
        return self

    def get_children(self, packet: Optional[Packet]=None) -> Iterator[Tuple[bytes, PacketAnalyzer]]:
        if packet is not None:
            return zip(packet.payloads, self._children)
        else:
            return iter((b'', child) for child in self._children)

    def encode_error_hook(self, visitor: PacketVisitor, exc: AssertionError, data: bytes, called_line: str) -> None:
        print('Warning: There may be differences in compression results:\n', called_line, file=sys.stderr)
        self.decode_on(visitor, data)
        self.encode_on(visitor)

    def print_packet(self, visitor: PacketVisitor) -> None:
        for child in self._children:
            child.print_packet(visitor)
        super().print_packet(visitor)


class Capsule(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(CapsuleID, raknet_capsule_codec)
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


class RakNetPacket(PacketAnalyzer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(RakNetPacketID, raknet_packet_codec)
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
        visitor.visit_decode_capsules(data, payload_length)

    def decode_on(self, visitor: PacketVisitor, data: bytes) -> None:
        def action():
            self._decode_raknet_packet(visitor, data)
            if len(self._children) > 0:
                self._decode_raknet_encapsulation(visitor)
        visitor.try_action(action, self.called_line)
