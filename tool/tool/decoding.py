"""
Debug tools for decoding.

When debugging, execute `from tool.decoding import *` in REPL.

>>> decode('840200000000480000000000003d3810')
[0] 840200000000480000000000003d3810
[1] FrameSet4(id=132, packet_sequence_num=2, payload=b'\\x00\\x00H\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[2] Unreliable(id=0, payload_length=72, payload=b'\\x00\\x00\\x00\\x00\\x00\\x00=8\\x10')
[3] ConnectedPing(id=0, ping_time_since_start=4012048)
>>> len(extract_chunk('full_chunk.txt'))
47
"""
import re
from binascii import unhexlify as unhex
from typing import List, Optional, Iterator

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
            bytes_data = eval(m[1])  # type: bytes
            length = len(bytes_data)
            return repr(bytes_data) if length <= bytes_mask_threshold else '[{} bytes]'.format(length)

        packet_str = str(packet).replace(r'\"', r'\x22').replace(r"\'", r'\x27')
        packet_str = _BYTES_REGEXP_FOR_SINGLE_QUOTE.sub(_summarize_bytes, packet_str)
        packet_str = _BYTES_REGEXP_FOR_DOUBLE_QUOTE.sub(_summarize_bytes, packet_str)
    else:
        packet_str = str(packet)
    return packet_str


class DecodeAgent:

    def __init__(self, verbose=True) -> None:
        self._verbose = verbose
        self._fragment = Fragment()
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

    def __iter__(self) -> Iterator[ValueObject]:
        for packet in self._packet:
            yield packet

    def clear(self):
        self.__init__(verbose=self._verbose)
        return self

    def _decode_raknet_packet(self, data: bytearray) -> None:
        context = CompositeCodecContext()
        packet = raknet_packet_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payload'):
            data = bytearray(packet.payload)
            while len(data) > 0:
                self._decode_raknet_frame(data)

    def _decode_raknet_frame(self, data: bytearray) -> None:
        context = CompositeCodecContext()
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
        elif self._verbose:
            print('FRAGMENT APPENDED')

    def _decode_connection_packet(self, data: bytearray) -> None:
        context = CompositeCodecContext()
        packet = connection_packet_codec.decode(data, context)
        self._packet.append(packet)
        del data[:context.length]
        if hasattr(packet, 'payloads'):
            for payload in packet.payloads:
                data = bytearray(payload)
                self._decode_game_packet(data)

    def _decode_game_packet(self, data: bytearray) -> None:
        context = CompositeCodecContext()
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


def extract_chunk(file_name: str) -> List[Chunk]:
    def generate_chunk() -> Iterator[Chunk]:
        with open(file_name, 'r') as file:
            _agent = DecodeAgent(verbose=False)
            for line in file.readlines():
                for packet in _agent.decode(line.strip()):
                    if packet.__class__.__name__ == 'FullChunkData':
                        yield decode_chunk(packet.data)
                _agent.clear()
    return list(generate_chunk())


def read_pcap(file_name: str) -> List[str]:
    import json
    import subprocess
    data = []

    def _collect_raknet_raw(o):
        if 'raknet_raw' in o:
            data.append(o['raknet_raw'][0])
        return o

    completed = subprocess.run('tshark -T jsonraw -r {}'.format(file_name), shell=True, stdout=subprocess.PIPE)
    json.loads(completed.stdout, object_hook=_collect_raknet_raw)
    return data


if __name__ == '__main__':
    import doctest
    doctest.testmod()
