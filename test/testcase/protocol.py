import inspect
import json
from os.path import dirname
from typing import NamedTuple as _NamedTuple
from unittest import TestCase

from pyminehub.mcpe.network import MCPEHandler
from pyminehub.network.address import Address
from pyminehub.raknet.frame import RakNetFrame as _RakNetFrame
# noinspection PyProtectedMember
from pyminehub.raknet.server import _RakNetServerProtocol
from util.codec import *
from util.mock import MockEventLoop, MockTransport, MockWorldProxy


def by_index(start: int, index: int) -> str:
    """Return label string.

    :param start: for example, 0x0c
    :param index: it is added to start value
    :return: for example, when start value is 0x0c and index is 1, return '0d:'
    """
    return '{:02x}:'.format(start + index)


class _ProtocolProxy:

    def __init__(self) -> None:
        self._queue = []  # type: List[Tuple[Address, bytes]]
        self._protocol = _RakNetServerProtocol(MockEventLoop(), MCPEHandler(MockWorldProxy()))
        self._protocol.connection_made(MockTransport(self._queue))

    def _get_packets(self):
        self._protocol.send_waiting_packets()
        d = defaultdict(list)
        for res_addr, res_data in self._queue:
            d[res_addr].append(res_data)
        self._queue.clear()
        return d

    def send(self, data_producer: Callable[[Address], str], from_: Address) -> Dict[Address, List[bytes]]:
        self._protocol.datagram_received(unhex(data_producer(from_)), from_)
        return self._get_packets()

    def next_moment(self) -> Dict[Address, List[bytes]]:
        self._protocol.next_moment()
        return self._get_packets()


class _ProtocolTestContext(AnalyzingContext):

    def __init__(self, test_case: TestCase) -> None:
        super().__init__()
        self._test_case = test_case

    def failure_exception(self, *args) -> Exception:
        return self._test_case.failureException(*args)

    def assert_equal(self, expected: T, actual: T, message: str= '') -> None:
        self._test_case.assertEqual(expected, actual, message)


class _TestDataProducer(Callable[[Address], str]):

    def __init__(self, context: _ProtocolTestContext, producer: Callable[[Address], str]) -> None:
        self._context = context
        self._producer = producer

    def __call__(self, addr: Address) -> str:
        return self._producer(addr)

    def get_context(self) -> _ProtocolTestContext:
        return self._context


class _TestData:

    def __init__(self, context: _ProtocolTestContext, json_dict: Dict) -> None:
        self._context = context
        self._json_dict = json_dict

    def that_is(self, name: str) -> _TestDataProducer:
        def producer(addr: Address) -> str:
            return self._json_dict[name]['client']['{}:{}'.format(*addr)].pop(0)
        return _TestDataProducer(self._context, producer)

    def that_is_response_of(self, name: str) -> _TestDataProducer:
        def producer(addr: Address) -> str:
            return self._json_dict[name]['server']['{}:{}'.format(*addr)].pop(0)
        return _TestDataProducer(self._context, producer)


_DecodingInfo = _NamedTuple('PacketInfo', [
    ('packet', ValueObject),
    ('data', bytes),
    ('called', str),
    ('packet_str', str)
])


class _DynamicValue(_NamedTuple('DynamicValue', [])):

    def __repr__(self) -> str:
        return 'DYNAMIC'


DYNAMIC = _DynamicValue()


class _PacketReplacer(AnalyzingVisitor):
    """Replace attribute values on sending packet."""

    def __init__(self, context: AnalyzingContext) -> None:
        self._context = context
        self._data = b''  # type: bytes

    def get_context(self) -> AnalyzingContext:
        return self._context

    def get_data(self) -> bytes:
        return self._data

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        self.get_context().assert_equal(expected, actual, message + '\n  when replacing')

    def assert_equal_for_encoding(self, expected: T, actual: T, message: str= '') -> None:
        pass

    def visit_after_decoding(
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs
    ) -> ValueObject:
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)

    def visit_after_encoding(self, packet: ValueObject, data: bytes, packet_str: str, called: str) -> None:
        self._data = data


class _PacketCollector(AnalyzingVisitor):

    def __init__(self, context: _ProtocolTestContext) -> None:
        self._context = context
        self._packets = []

    def get_context(self) -> _ProtocolTestContext:
        return self._context

    def get_packets(self) -> Tuple[ValueObject, ...]:
        return tuple(reversed(self._packets))

    def get_name(self) -> str:
        raise NotImplementedError()

    def append_fragment(self, frame: _RakNetFrame) -> Optional[bytes]:
        return self.get_context().append_fragment(self.get_name(), frame)

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        self.get_context().assert_equal(expected, actual,
                                        message + '\n  when decoding {} data'.format(self.get_name()))

    def assert_equal_for_encoding(self, expected: T, actual: T, message: str= '') -> None:
        pass

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        pass

    def replace_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        return packet

    def _replace_dynamic_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        dynamic_args = dict((key, value) for key, value in kwargs.items() if value is DYNAMIC)
        dynamic_values = dict((key, getattr(packet, key)) for key, value in dynamic_args.items())
        self.dynamic_value_found(dynamic_values)
        for key in dynamic_args:
            del kwargs[key]
        # noinspection PyProtectedMember
        return packet._replace(**dynamic_args)

    @staticmethod
    def _replace_payload(packet: ValueObject) -> ValueObject:
        if hasattr(packet, 'payload'):
            # noinspection PyProtectedMember
            return packet._replace(payload='[mask]')
        if hasattr(packet, 'payloads'):
            # noinspection PyProtectedMember
            return packet._replace(payloads='[mask]')
        return packet

    # noinspection PyMethodOverriding
    def visit_after_decoding(
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs
    ) -> ValueObject:
        """Collect packets whose attributes is replaced with kwargs."""
        tmp_packet = self._replace_dynamic_values(packet, kwargs)
        tmp_packet = self._replace_payload(tmp_packet)
        tmp_packet = self.replace_values(tmp_packet, kwargs)
        self._packets.append(_DecodingInfo(tmp_packet, data, called, '  ' + packet_str))
        return packet


class _ExpectedPacketCollector(_PacketCollector):

    def get_name(self) -> str:
        return 'expected'

    def replace_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)


class _ActualPacketCollector(_PacketCollector):

    def get_name(self) -> str:
        return 'actual'

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        self.get_context().update(dynamic_values)


class EncodedData:

    def __init__(self, data_producer: _TestDataProducer) -> None:
        """Encoded data validator.

        :param data_producer: data that decode to packet
        """
        self._data_producer = data_producer
        self._analyzer = None

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    def __call__(self, addr: Address) -> str:
        def replace_packet_attributes():
            self._analyzer.decode_on(visitor, unhex(self._data_producer(addr)))
            self._analyzer.encode_on(visitor)
        visitor = _PacketReplacer(self._data_producer.get_context())
        try_action(replace_packet_attributes, exception_factory=self._data_producer.get_context().failure_exception)
        return visitor.get_data().hex()

    def collect_packet(self, actual_data: bytes, addr: Address) -> Tuple[List[ValueObject], List[ValueObject]]:
        context = self._data_producer.get_context()
        collector_for_expected = _ExpectedPacketCollector(context)
        collector_for_actual = _ActualPacketCollector(context)
        self._analyzer.decode_on(collector_for_expected, unhex(self._data_producer(addr)))
        self._analyzer.decode_on(collector_for_actual, actual_data)
        return list(collector_for_expected.get_packets()), list(collector_for_actual.get_packets())


class ProtocolTestCase(TestCase):

    _JSON_IMPORT_KEY = '__import__'

    def __init__(self, method_name: str) -> None:
        super().__init__(method_name)
        self.context = _ProtocolTestContext(self)

    def _get_file_name(self, test_name: str) -> str:
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), 'protocol_data', test_name, 'json')

    def _import_json(self, test_name_list: List[str]) -> Dict:
        data_json = {}
        for test_name in test_name_list:
            with open(self._get_file_name(test_name), 'r') as file:
                data_json.update(json.load(file))
        return data_json

    def _load_data(self) -> _TestData:
        with open(self._get_file_name(self._testMethodName), 'r') as file:
            data_json = json.load(file)
            if self._JSON_IMPORT_KEY in data_json:
                data_json.update(self._import_json(data_json[self._JSON_IMPORT_KEY]))
                del data_json[self._JSON_IMPORT_KEY]
            return _TestData(self.context, data_json)

    def setUp(self) -> None:
        if self._testMethodName not in type(self).__dict__:
            self.skipTest('This test is defined in super class.')
        self.proxy = _ProtocolProxy()
        self.data = self._load_data()

    def tearDown(self) -> None:
        self.proxy = None
        self.data = None
        self.context = None

    def assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        try_action(lambda: self._assert_that(actual, expected), exception_factory=self.failureException)

    def _assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        for addr in expected:
            self.assertTrue(addr in actual,
                            'Clients specified by the address {} did not receive packets.'.format(addr))
            expected_data_list = expected[addr]
            actual_data_list = actual[addr]
            for expected_data, actual_data in zip(expected_data_list, actual_data_list):
                self._assert_equal(actual_data, expected_data, addr)
            self.assertEqual(
                len(expected_data_list), len(actual_data_list),
                '\n'.join(list(data.hex() for data in actual_data_list)))
        self.assertEqual(set(), set(actual.keys()) - set(expected.keys()),
                         'Excessive packets are being sent.')

    def _assert_equal(self, actual: bytes, expected: EncodedData, addr: Address) -> None:
        expected_packets, actual_packets = expected.collect_packet(actual, addr)
        for expected, actual in zip(expected_packets, actual_packets):
            def action():
                self.assertEqual(expected.packet, actual.packet,
                                 "Actual data is '{}'".format(actual.data.hex()))
            try_action(action, called_line=actual.called, packet_info=actual.packet_str)
        self.assertEqual(len(expected_packets), len(actual_packets),
                         'Following packets were left:\n'
                         '\n'.join(str(p) for p in actual_packets[len(expected_packets):]))
