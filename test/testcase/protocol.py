import inspect
import json
from binascii import unhexlify as unhex
from collections import defaultdict
from os.path import dirname
from typing import List, Dict
from unittest import TestCase

from pyminehub.mcpe.network import MCPEHandler
from pyminehub.network.address import Address
# noinspection PyProtectedMember
from pyminehub.raknet.server import _RakNetServerProtocol
from util.codec import *
from util.mock import MockEventLoop, MockTransport


class _TestData:

    def __init__(self, json_dict: Dict) -> None:
        self._json_dict = json_dict

    def that_is(self, name: str) -> Callable[[Address], str]:
        def producer(addr: Address) -> str:
            return self._json_dict[name]['client']['{}:{}'.format(*addr)].pop(0)
        return producer

    def that_is_response_of(self, name: str) -> Callable[[Address], str]:
        def producer(addr: Address) -> str:
            return self._json_dict[name]['server']['{}:{}'.format(*addr)].pop(0)
        return producer


class _ProtocolProxy:

    def __init__(self) -> None:
        self._queue = []  # type: List[Tuple[Address, bytes]]
        self._protocol = _RakNetServerProtocol(MockEventLoop(), MCPEHandler())
        self._protocol.connection_made(MockTransport(self._queue))

    def send(self, data_producer: Callable[[Address], str], from_: Address) -> Dict[Address, List[bytes]]:
        self._protocol.datagram_received(unhex(data_producer(from_)), from_)
        self._protocol.send_waiting_packets()
        d = defaultdict(list)
        for res_addr, res_data in self._queue:
            d[res_addr].append(res_data)
        self._queue.clear()
        return d


class _PacketCollector(PacketVisitor):

    def __init__(self, test_case: TestCase, name: str) -> None:
        self._test_case = test_case
        self._name = name
        self._packets = []

    def get_packets(self) -> Tuple[Packet, ...]:
        return tuple(reversed(self._packets))

    def visit_decode_capsules(self, data: bytes, decoded_payload_length: int) -> None:
        self._test_case.assertEqual(
            len(data), decoded_payload_length, '  when decoding {} data'.format(self._name))

    # noinspection PyMethodOverriding
    def visit_decode_task(
            self, packet_id_cls: PacketID, packet: Packet, data: bytes, called: str, packet_str: str,
            context: PacketCodecContext, children_num: int, packet_id: PacketID, **kwargs) -> None:
        """Collect packets whose attributes is replaced with kwargs."""
        self._test_case.assertEqual(
            packet_id, packet_id_cls(packet.id), '  when decoding {} data'.format(self._name))
        if packet_id_cls != CapsuleID:
            self._test_case.assertEqual(len(data), context.length)
        if hasattr(packet, 'payloads'):
            self._test_case.assertEqual(children_num, len(packet.payloads))
        if hasattr(packet, 'payload'):
            kwargs['payload'] = '[mask]'
        # noinspection PyProtectedMember
        self._packets.append((packet._replace(**kwargs), called, packet_str))

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, called: str, packet_str: str) -> None:
        pass


class EncodedData:

    def __init__(self, expected_data_producer: Callable[[Address], str]) -> None:
        """Encoded data validator.

        :param expected_data_producer: expected data that decode to packet
        """
        self._expected_data_producer = expected_data_producer
        self._analyzer = None

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    def collect_packet(
            self, expected: _PacketCollector, actual: _PacketCollector, actual_data: bytes, addr: Address) -> None:
        self._analyzer.decode_on(expected, unhex(self._expected_data_producer(addr)))
        self._analyzer.decode_on(actual, actual_data)


class ProtocolTestCase(TestCase):

    def _get_file_name(self) -> str:
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), 'protocol_data', self._testMethodName, 'json')

    def setUp(self) -> None:
        self.proxy = _ProtocolProxy()
        with open(self._get_file_name(), 'r') as file:
            self.data = _TestData(json.load(file))

    def tearDown(self) -> None:
        self.proxy = None

    def assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        try_action(lambda: self._assert_that(actual, expected), exception_factory=self.failureException)

    def _assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        self.assertEqual(set(expected.keys()), set(actual.keys()))
        for addr in expected:
            expected_data_list = expected[addr]
            actual_data_list = actual[addr]
            self.assertEqual(len(expected_data_list), len(actual_data_list))
            for expected_data in expected_data_list:
                self._assert_equals(actual_data_list.pop(0), expected_data, addr)

    def _assert_equals(self, actual: bytes, expected: EncodedData, addr: Address) -> None:
        collector_for_expected = _PacketCollector(self, 'expected')
        collector_for_actual = _PacketCollector(self, 'actual')
        expected.collect_packet(collector_for_expected, collector_for_actual, actual, addr)
        for expected, actual in zip(collector_for_expected.get_packets(), collector_for_actual.get_packets()):
            try_action(lambda: self.assertEqual(expected[0], actual[0]),
                       called_line=actual[1], packet_info=actual[2])
