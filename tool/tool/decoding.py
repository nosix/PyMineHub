"""
Debug tools for decoding.

When debugging, execute `from tool.decoding import *` in REPL.

>>> decode('840200000000480000000000003d3810')
[0] 840200000000480000000000003d3810
[1] FrameSet4(id=132, packet_sequence_num=2, payload=b'\\x00\\x00H\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[2] Unreliable(id=0, payload_length=72, payload=b'\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[3] ConnectedPing(id=0, ping_time_since_start=4012048)
>>> len(extract_chunk(load_packets('mppm_login_logout.txt')))
223
"""
import re
from binascii import unhexlify as unhex
from typing import NamedTuple as _NamedTuple, Iterator, List, Optional, Union

from pyminehub.binutil.composite import CompositeCodecContext
from pyminehub.mcpe.chunk import Chunk, decode_chunk
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.raknet.codec import raknet_packet_codec, raknet_frame_codec
from pyminehub.raknet.fragment import Fragment
from pyminehub.raknet.frame import RakNetFrameType
from pyminehub.value import ValueObject

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
            bytes_data = eval(m.group(1))  # type: bytes
            length = len(bytes_data)
            return repr(bytes_data) if length <= bytes_mask_threshold else '[{} bytes]'.format(length)

        packet_str = str(packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
        packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(_summarize_bytes, packet_str)
        packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(_summarize_bytes, packet_str)
    else:
        packet_str = str(packet)
    return packet_str


_TaggedData = _NamedTuple('TaggedData', [('tag', str), ('data', str)])


class DecodeAgent:

    def __init__(self, verbose=True) -> None:
        self._verbose = verbose
        self._fragment = Fragment()
        self._items = []  # type: List[Union[str, _TaggedData, ValueObject]]
        self._decode_func = [
            self._decode_raknet_packet,
            self._decode_raknet_frame,
            self._decode_connection_packet,
            self._decode_game_packet]

    def __repr__(self) -> str:
        def to_str(item: Union[str, _TaggedData, ValueObject]) -> str:
            if isinstance(item, str):
                return item
            if isinstance(item, _TaggedData):
                return ': '.join(item)
            if isinstance(item, ValueObject):
                return get_packet_str(item)
            raise AssertionError()
        return '\n'.join('[{}] {}'.format(i, to_str(item)) for i, item in enumerate(self._items))

    def __getitem__(self, index: int) -> Union[bytes, ValueObject]:
        item = self._items[index]
        if isinstance(item, str):
            return unhex(item)
        if isinstance(item, _TaggedData):
            # noinspection PyUnresolvedReferences
            return unhex(item.data)  # FIXME why inspection report warning?
        if isinstance(item, ValueObject):
            return item
        raise AssertionError()

    def __iter__(self) -> Iterator[ValueObject]:
        for item in self._items:
            if isinstance(item, ValueObject):
                yield item

    def clear(self):
        self.__init__(verbose=self._verbose)
        return self

    def _decode_raknet_packet(self, data: bytearray) -> None:
        context = CompositeCodecContext()
        packet = raknet_packet_codec.decode(data, context)
        self._items.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payload'):
            data = bytearray(packet.payload)
            while len(data) > 0:
                self._decode_raknet_frame(data)

    def _decode_raknet_frame(self, data: bytearray) -> None:
        context = CompositeCodecContext()
        packet = raknet_frame_codec.decode(data, context)
        self._items.append(packet)
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
        elif self._verbose:
            print('FRAGMENT APPENDED')

    def _decode_connection_packet(self, data: bytearray) -> None:
        context = CompositeCodecContext()
        packet = connection_packet_codec.decode(data, context)
        self._items.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payloads'):
            for payload in packet.payloads:
                data = bytearray(payload)
                self._decode_game_packet(data)

    def _decode_game_packet(self, data: bytearray) -> None:
        context = CompositeCodecContext()
        packet = game_packet_codec.decode(data, context)
        self._items.append(packet)
        del data[:context.length]

    def decode(self, data: str, depth: int=0, tag: str=None):
        self._items.append(data if tag is None else _TaggedData(tag, data))
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


def load_raknet_raw(pcap_file_name: str) -> List[str]:
    import json
    import subprocess
    data = []
    port_data_pair = None

    def _collect_raknet_raw(o):
        nonlocal port_data_pair
        if 'udp.srcport_raw' in o:
            port_data_pair = [o['udp.srcport_raw'][0]]
        if 'frame_raw' in o:
            assert port_data_pair is not None
            port_data_pair.append(o['frame_raw'][0][84:])  # 84 is header size times 2
            data.append('\t'.join(port_data_pair))
        return o

    completed = subprocess.run('tshark -T jsonraw -r {}'.format(pcap_file_name), shell=True, stdout=subprocess.PIPE)
    json.loads(completed.stdout, object_hook=_collect_raknet_raw)
    return data


def load_packets(raknet_raw_file_name: str) -> DecodeAgent:
    import struct
    _agent = DecodeAgent(verbose=False)
    with open(raknet_raw_file_name, 'r') as file:
        for i, line in enumerate(file.readlines()):
            try:
                port_raw, data_raw = line.split()
                port, = struct.unpack('!H', unhex(port_raw))  # Don't remove comma, to get first one
                _agent.decode(data_raw, tag=str(port))
            except Exception as exc:
                exc.args = ('{}, line {}, in {}'.format(exc.args[0], i + 1, raknet_raw_file_name), )
                import traceback
                traceback.print_exc()
    return _agent


def extract_chunk(packet_list: Iterator[ValueObject]) -> List[Chunk]:
    def generate_chunk() -> Iterator[Chunk]:
        for packet in packet_list:
            if packet.__class__.__name__ == 'FullChunkData':
                yield decode_chunk(packet.data)
    return list(generate_chunk())


if __name__ == '__main__':
    import doctest
    doctest.testmod()
