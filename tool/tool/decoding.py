"""
Debug tools for decoding.

When debugging, execute `from tool.decoding import *` in REPL.

>>> decode('840200000000480000000000003d3810')
[0] 840200000000480000000000003d3810
[1] PacketFrameSet4(type=<RakNetPacketType.FRAME_SET_4: 132>, packet_sequence_num=2, payload=b'\\x00\\x00H\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[2] FrameUnreliable(type=<RakNetFrameType.UNRELIABLE: 0>, payload_length=72, payload=b'\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[3] PacketConnectedPing(type=<ConnectionPacketType.CONNECTED_PING: 0>, ping_time_since_start=4012048)
>>> len(extract_chunk(load_packets('mppm_login_logout.txt')))
224
"""
import re
from binascii import unhexlify as unhex
from typing import NamedTuple as _NamedTuple, Iterator, List, Optional, Union, Sequence

from pyminehub.binutil.composite import CompositeCodecContext
from pyminehub.mcpe.chunk import Chunk, decode_chunk
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketType, GamePacketType
from pyminehub.raknet.codec import raknet_packet_codec, raknet_frame_codec
from pyminehub.raknet.fragment import Fragment
from pyminehub.raknet.frame import RakNetFrameType
from pyminehub.raknet.packet import RakNetPacketType
from pyminehub.value import ValueObject, ValueType

_ASCII_CHARS = set(c for c in range(0x20, 0x7f))
_ASCII_CHARS_FOR_DOUBLE_QUOTE = _ASCII_CHARS - {0x22, 0x5c, 0x5d}  # " - \
_ASCII_CHARS_FOR_SINGLE_QUOTE = _ASCII_CHARS - {0x27, 0x5c, 0x5d}  # ' - \
_BYTES_REGEXP_FOR_DOUBLE_QUOTE = re.compile(
    r'(b"[{}\-\\\]]*?")'.format(''.join(chr(c) for c in _ASCII_CHARS_FOR_DOUBLE_QUOTE)))
_BYTES_REGEXP_FOR_SINGLE_QUOTE = re.compile(
    r"(b'[{}\-\\\]]*?')".format(''.join(chr(c) for c in _ASCII_CHARS_FOR_SINGLE_QUOTE)))


def _replace_bytes(s: str, bytes_mask_threshold: int) -> str:
    """
    >>> b = b"'\\xb8|T\\xfb'\\xb8\\xa8\\xfd+9'</\\xe8\\x0b"
    >>> _replace_bytes(str(b), 0)
    '[16 bytes]'
    >>> _replace_bytes(str(b) + str(b), 0)
    '[16 bytes][16 bytes]'
    >>> _replace_bytes("name='PyMineHub', value='something'", 0)  # FIXME
    "name='PyMineHub', value='something'"
    """
    def _summarize_bytes(bytes_str: str) -> str:
        bytes_data = eval(bytes_str)  # type: bytes
        length = len(bytes_data)
        return repr(bytes_data) if length <= bytes_mask_threshold else '[{} bytes]'.format(length)

    s = s.replace(r'\"', r'\x22').replace(r"\'", r'\x27')

    start = 0
    while True:
        d_match = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.search(s, start)
        s_match = _BYTES_REGEXP_FOR_SINGLE_QUOTE.search(s, start)
        d_start = len(s) if d_match is None else d_match.start()
        s_start = len(s) if s_match is None else s_match.start()
        if d_start == s_start:
            break
        match = d_match if d_start < s_start else s_match
        summarized_bytes_str = _summarize_bytes(s[match.start():match.end()])
        s = s[0:match.start()] + summarized_bytes_str + s[match.end():]
        start = match.start() + len(summarized_bytes_str)
    return s


def get_packet_str(packet: ValueObject, bytes_mask_threshold: Optional[int]=16) -> str:
    return str(packet) if bytes_mask_threshold is None else _replace_bytes(str(packet), bytes_mask_threshold)


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
            if isinstance(item, _TaggedData):  # since ValueObject is tuple, it also matches TaggedData
                continue
            if isinstance(item, ValueObject):
                yield item

    def clear(self):
        self.__init__(verbose=self._verbose)
        return self

    def drop(self, drop_type: ValueType) -> 'DecodeAgent':
        self._items = list(item for item in self._items
                           if not isinstance(item, ValueObject) or item.type not in drop_type)
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

        if packet.type == RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT:
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
    """Decode data.

    :param data: decoded data corresponding to depth
    :param depth: 0 - RakNetPacket, 1 - RakNetFrame, 2 - ConnectionPacket, 3 - GamePacket
    """
    return agent.decode(data, depth)


def clear() -> DecodeAgent:
    return agent.clear()


def drop(*depth: int) -> DecodeAgent:
    """Drop decoded result at the specified depth.

    :param depth: 0 - RakNetPacket, 1 - RakNetFrame, 2 - ConnectionPacket, 3 - GamePacket
    """
    drop_type = [RakNetPacketType, RakNetFrameType, ConnectionPacketType, GamePacketType]
    for d in depth:
        agent.drop(drop_type[d])
    return agent


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
            port_data_pair.append(o['frame_raw'][0])
        if 'raknet_raw' in o:
            assert port_data_pair is not None
            raknet_raw = o['raknet_raw'][0]
            frame_raw = port_data_pair.pop()
            port_data_pair.append(frame_raw[frame_raw.find(raknet_raw):])
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
                _agent.decode(data_raw, tag='L{}:{}'.format(i+1, port))
            except Exception as exc:
                exc.args = ('{}, line {}, in {}'.format(exc.args[0], i + 1, raknet_raw_file_name), )
                import traceback
                traceback.print_exc()
    return _agent


def extract_chunk(packet_list: Iterator[ValueObject]) -> List[Chunk]:
    def generate_chunk() -> Iterator[Chunk]:
        for packet in packet_list:
            if packet.__class__.__name__ == 'PacketFullChunkData':
                yield decode_chunk(packet.data)
    return list(generate_chunk())


_FILTER_PREFIX = (
    'FrameSet',
    'Reliable',
    'Unreliable',
    'Batch',
    'Ack',
    'UnconnectedPing',
    'UnconnectedPong',
    'ConnectedPing',
    'ConnectedPong',
    'FullChunk',
    'SetTime',
)


def extract_packet(pcap_file_name: str, filter_prefix: Sequence[str]=_FILTER_PREFIX) -> None:
    import re
    regexp = re.compile('^({})'.format('|'.join(filter_prefix)))
    import os.path
    basename = os.path.splitext(os.path.basename(pcap_file_name))[0]
    intermediate_file_name = basename + '.txt'
    with open(intermediate_file_name, 'w') as file:
        for line in load_raknet_raw(pcap_file_name):
            print(line, file=file)
    summary_file_name = 'summary_' + intermediate_file_name
    with open(summary_file_name, 'w') as file:
        for p in load_packets(intermediate_file_name):
            if regexp.match(p.__class__.__name__):
                continue
            print(p, file=file)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
