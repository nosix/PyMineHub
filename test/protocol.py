from binascii import unhexlify as unhex
from collections import defaultdict
from typing import List, Dict
from unittest import TestCase

from pyminehub.debug.codec import *
from pyminehub.mcpe.network import MCPEHandler
from pyminehub.network.address import Address
# noinspection PyProtectedMember
from pyminehub.raknet.server import _RakNetServerProtocol
from util.mock import MockEventLoop, MockTransport


class _ProtocolProxy:

    def __init__(self) -> None:
        self._queue = []  # type: List[Tuple[Address, bytes]]
        self._protocol = _RakNetServerProtocol(MockEventLoop(), MCPEHandler())
        self._protocol.connection_made(MockTransport(self._queue))

    def send(self, addr: Address, data: str) -> Dict[Address, List[bytes]]:
        self._protocol.datagram_received(unhex(data), addr)
        d = defaultdict(list)
        for res_addr, res_data in self._queue:
            d[res_addr].append(res_data)
        self._queue.clear()
        return d


class _PacketCollector(PacketVisitor):

    def __init__(self) -> None:
        self._packets = []

    def get_packets(self) -> Tuple[Packet, ...]:
        return tuple(self._packets)

    def visit_decode_capsules(self, data: bytes, decoded_payload_length: int) -> None:
        pass

    def visit_decode_task(
            self, packet_id_cls: PacketID, packet: Packet, data: bytes,
            context: PacketCodecContext, *args, **kwargs) -> None:
        """Collect packets whose attributes is replaced with kwargs."""
        # noinspection PyProtectedMember
        self._packets.append(packet._replace(**kwargs))

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        pass


class EncodedData:

    def __init__(self, expected_data: str) -> None:
        """Encoded data validator.

        :param expected_data: expected data that decode to packet
        """
        self._expected_data = unhex(expected_data)
        self._analyzer = None

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    def collect_packet(self, expected: _PacketCollector, actual: _PacketCollector, actual_data: bytes) -> None:
        self._analyzer.decode_on(expected, self._expected_data)
        self._analyzer.decode_on(actual, actual_data)


class ProtocolTestCase(TestCase):

    def setUp(self) -> None:
        self.proxy = _ProtocolProxy()

    def tearDown(self) -> None:
        self.proxy = None

    def assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        self.assertEqual(set(expected.keys()), set(actual.keys()))
        for addr in expected:
            expected_data_list = expected[addr]
            actual_data_list = actual[addr]
            self.assertEqual(len(expected_data_list), len(actual_data_list))
            for expected_data in expected_data_list:
                self._assert_equals(actual_data_list.pop(0), expected_data)

    def _assert_equals(self, actual: bytes, expected: EncodedData) -> None:
        collector_for_expected = _PacketCollector()
        collector_for_actual = _PacketCollector()
        expected.collect_packet(collector_for_expected, collector_for_actual, actual)
        for expected, actual in zip(collector_for_expected.get_packets(), collector_for_actual.get_packets()):
            self.assertEqual(expected, actual)
