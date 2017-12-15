import inspect
import json
from collections import defaultdict
from os.path import dirname
from typing import NamedTuple as _NamedTuple
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


DecodingInfo = _NamedTuple('PacketInfo', [
    ('packet', Packet),
    ('data', bytes),
    ('called', str),
    ('packet_str', str)
])


class DynamicValue(_NamedTuple('DynamicValue', [])):

    def __repr__(self) -> str:
        return 'DYNAMIC'


DYNAMIC = DynamicValue()


class _TestContext:

    def get_name(self) -> str:
        raise NotImplementedError()

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def replace_values(self, packet: Packet, kwargs: Dict[str, Any]) -> Packet:
        raise NotImplementedError()


class _ActualContext(_TestContext):

    def __init__(self, dynamic_values: Dict[str, Any]) -> None:
        self._dynamic_values = dynamic_values

    def get_name(self) -> str:
        return 'actual'

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        self._dynamic_values.update(dynamic_values)

    def replace_values(self, packet: Packet, kwargs: Dict[str, Any]) -> Packet:
        return packet


class _ExpectedContext(_TestContext):

    def get_name(self) -> str:
        return 'expected'

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        pass

    def replace_values(self, packet: Packet, kwargs: Dict[str, Any]) -> Packet:
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)


class _PacketReplacer(PacketVisitor):

    def __init__(self) -> None:
        self.data = b''  # type: bytes

    def assert_equal_for_encoding(self, expected: T, actual: T, message: str= '') -> None:
        pass

    def visit_after_decoding(
            self, data: bytes, packet_id: PacketID, packet: Packet, packet_str: str, called: str, **kwargs) -> Packet:
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)

    def visit_after_encoding(self, packet: Packet, data: bytes, packet_str: str, called: str) -> None:
        self.data = data


class _PacketCollector(PacketVisitor):

    _PAYLOAD_MASK = {'payload': '[mask]'}

    def __init__(self, test_case: TestCase, context: _TestContext) -> None:
        self._test_case = test_case
        self._context = context
        self._packets = []

    def get_packets(self) -> Tuple[Packet, ...]:
        return tuple(reversed(self._packets))

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        self._test_case.assertEqual(
            expected, actual, message + '\n  when decoding {} data'.format(self._context.get_name()))

    def _replace_dynamic_values(self, packet: Packet, kwargs: Dict[str, Any]) -> Packet:
        dynamic_args = dict((key, value) for key, value in kwargs.items() if value is DYNAMIC)
        dynamic_values = dict((key, getattr(packet, key)) for key, value in dynamic_args.items())
        self._context.dynamic_value_found(dynamic_values)
        for key in dynamic_args:
            del kwargs[key]
        # noinspection PyProtectedMember
        return packet._replace(**dynamic_args)

    def _replace_payload(self, packet: Packet) -> Packet:
        if hasattr(packet, 'payload'):
            # noinspection PyProtectedMember
            return packet._replace(**self._PAYLOAD_MASK)
        else:
            return packet

    # noinspection PyMethodOverriding
    def visit_after_decoding(
            self, data: bytes, packet_id: PacketID, packet: Packet, packet_str: str, called: str, **kwargs) -> Packet:
        """Collect packets whose attributes is replaced with kwargs."""
        tmp_packet = self._replace_dynamic_values(packet, kwargs)
        tmp_packet = self._replace_payload(tmp_packet)
        tmp_packet = self._context.replace_values(tmp_packet, kwargs)
        self._packets.append(DecodingInfo(tmp_packet, data, called, '  ' + packet_str))
        return packet


class EncodedData:

    def __init__(self, data_producer: Callable[[Address], str]) -> None:
        """Encoded data validator.

        :param data_producer: data that decode to packet
        """
        self._data_producer = data_producer
        self._analyzer = None

    def __call__(self, addr: Address) -> str:
        def action():
            self._analyzer.decode_on(visitor, unhex(self._data_producer(addr)))
            self._analyzer.encode_on(visitor)
        visitor = _PacketReplacer()
        try_action(action, exception_factory=Exception)
        return visitor.data.hex()

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    def collect_packet(
            self, expected: _PacketCollector, actual: _PacketCollector, actual_data: bytes, addr: Address) -> None:
        self._analyzer.decode_on(expected, unhex(self._data_producer(addr)))
        self._analyzer.decode_on(actual, actual_data)


class ProtocolTestCase(TestCase):

    def __init__(self, method_name: str) -> None:
        super().__init__(method_name)
        self.values = {}  # type: Dict[str, Any]

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
            self.assertEqual(
                len(expected_data_list), len(actual_data_list),
                '\n'.join(list(data.hex() for data in actual_data_list)))
            for expected_data in expected_data_list:
                self._assert_equals(actual_data_list.pop(0), expected_data, addr)

    def _assert_equals(self, actual: bytes, expected: EncodedData, addr: Address) -> None:
        collector_for_expected = _PacketCollector(self, _ExpectedContext())
        collector_for_actual = _PacketCollector(self, _ActualContext(self.values))
        expected.collect_packet(collector_for_expected, collector_for_actual, actual, addr)
        expected_packets = list(collector_for_expected.get_packets())
        actual_packets = list(collector_for_actual.get_packets())
        self.assertEqual(len(expected_packets), len(actual_packets))
        for expected, actual in zip(expected_packets, actual_packets):
            def action():
                self.assertEqual(expected.packet, actual.packet, "Actual data is '{}'".format(actual.data.hex()))
            try_action(action, called_line=actual.called, packet_info=actual.packet_str)
