import asyncio
import inspect
import json
import os
from binascii import unhexlify as unhex
from os.path import dirname
from typing import NamedTuple as _NamedTuple
from unittest import TestCase

from pyminehub.mcpe.network import MCPEHandler
from pyminehub.network.address import Address
from pyminehub.raknet.frame import RakNetFrame as _RakNetFrame
# noinspection PyProtectedMember
from pyminehub.raknet.server import _RakNetProtocolImpl
from util.codec import *
from util.mock import MockEventLoop, MockTransport, MockWorldProxy


def by_index(start: int, index: int) -> str:
    """Return label string.

    :param start: for example, 0x0c
    :param index: it is added to start value
    :return: for example, when start value is 0x0c and index is 1, return '0d:'
    """
    return '{:02x}:'.format(start + index)


ReceivedData = Dict[Address, List[bytes]]


def print_data(data: ReceivedData, addr: Address) -> None:
    print('\n'.join(p.hex() for p in data[addr]))


class _ProtocolMockEventLoop(MockEventLoop):

    def __init__(self):
        self._loop_to_update_coro = None
        self._loop_to_send_coro = []

    def next_moment(self):
        self._loop_to_update_coro.send(None)

    def send_waiting_packets(self):
        for coro in self._loop_to_send_coro:
            try:
                coro.send(None)
            except AssertionError as exc:
                if exc.args[0].startswith('yield from'):
                    raise AssertionError('no more received data') from None

    def create_task(self, coro):
        if coro.__name__ == 'loop_to_update':
            self._loop_to_update_coro = coro
        if coro.__name__ == 'loop_to_send':
            self._loop_to_send_coro.append(coro)
        return asyncio.Task(coro)


class _ProtocolMockTransport(MockTransport):

    def __init__(self, queue: List[Tuple[Address, bytes]]):
        super().__init__()
        self._queue = queue

    def sendto(self, data: bytes, addr: Address=None) -> None:
        self._queue.append((addr, data))


class _ProtocolProxy:

    def __init__(self) -> None:
        self._queue = []  # type: List[Tuple[Address, bytes]]
        self._loop = _ProtocolMockEventLoop()
        self._proxy = MockWorldProxy()
        self._protocol = _RakNetProtocolImpl(self._loop, MCPEHandler(self._proxy))
        self._protocol.connection_made(_ProtocolMockTransport(self._queue))

    @staticmethod
    def close() -> None:
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def receive(self):
        self._loop.send_waiting_packets()
        d = defaultdict(list)
        for res_addr, res_data in self._queue:
            d[res_addr].append(res_data)
        self._queue.clear()
        return d

    def send(self, data_producer: Callable[[Address], str], from_: Address) -> None:
        self._protocol.datagram_received(unhex(data_producer(from_)), from_)

    def next_moment(self) -> None:
        self._proxy.put_next_event()
        self._loop.next_moment()


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

    @property
    def created(self) -> _TestDataProducer:
        return _TestDataProducer(self._context, lambda addr: '')

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


def _capture_dynamic_value(
        packet: ValueObject, kwargs: dict, dynamic_value_found: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
    dynamic_args = dict((key, value) for key, value in kwargs.items() if value is DYNAMIC)
    dynamic_values = dict((key, getattr(packet, key)) for key, value in dynamic_args.items())
    dynamic_value_found(dynamic_values)
    for key in dynamic_args:
        del kwargs[key]
    return dynamic_args


class Replace:

    def __init__(self, pattern: str, repl: str) -> None:
        self._pattern = pattern
        self._repl = repl

    def replace(self, value: str) -> Tuple[str, str]:
        replaced = ''

        def capture(m):
            nonlocal replaced
            replaced = m.group(0)
            return self._repl

        return re.sub(self._pattern, capture, value), replaced


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

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        self.get_context().update(dynamic_values)

    def visit_after_decoding(
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs
    ) -> ValueObject:
        _capture_dynamic_value(packet, kwargs, self.dynamic_value_found)
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)

    def visit_after_encoding(self, packet: ValueObject, data: bytes, packet_str: str, called: str) -> None:
        self._data = data


class _PacketCollector(AnalyzingVisitor):

    _MASK_ATTRIBUTE = ('payload', 'payloads', 'payload_length')

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

    @staticmethod
    def _remove_replace_pattern(kwargs: Dict[str, Any]) -> Dict[str, Replace]:
        replace_args = dict((key, value) for key, value in kwargs.items() if isinstance(value, Replace))
        for key in replace_args:
            del kwargs[key]
        return replace_args

    def _replace_pattern(self, packet: ValueObject, replace_pattern: Dict[str, Replace]) -> str:
        replaced_dict = {}
        packet_str = str(packet)
        for key, pattern in replace_pattern.items():
            packet_str, replaced = pattern.replace(packet_str)
            replaced_dict[key] = replaced
        self.dynamic_value_found(replaced_dict)
        return packet_str

    def _replace_dynamic_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        dynamic_args = _capture_dynamic_value(packet, kwargs, self.dynamic_value_found)
        # noinspection PyProtectedMember
        return packet._replace(**dynamic_args)

    def _replace_payload(self, packet: ValueObject) -> ValueObject:
        kwargs = dict((name, '[mask]') for name in self._MASK_ATTRIBUTE if hasattr(packet, name))
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)

    # noinspection PyMethodOverriding
    def visit_after_decoding(
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs
    ) -> ValueObject:
        """Collect packets whose attributes is replaced with kwargs."""
        replace_pattern = self._remove_replace_pattern(kwargs)
        tmp_packet = self._replace_dynamic_values(packet, kwargs)
        tmp_packet = self.replace_values(tmp_packet, kwargs)
        tmp_packet = self._replace_payload(tmp_packet)
        tmp_packet_str = self._replace_pattern(tmp_packet, replace_pattern)
        self._packets.append(_DecodingInfo(tmp_packet_str, data, called, '  ' + packet_str))
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
            # noinspection PyArgumentList
            data = self._data_producer(addr)
            if data:
                self._analyzer.decode_on(visitor, unhex(data))
            else:
                self._analyzer.create(visitor)
            self._analyzer.encode_on(visitor)
        visitor = _PacketReplacer(self._data_producer.get_context())
        try_action(replace_packet_attributes, exception_factory=self._data_producer.get_context().failure_exception)
        return visitor.get_data().hex()

    def collect_packet(self, actual_data: bytes, addr: Address) -> Tuple[List[ValueObject], List[ValueObject]]:
        context = self._data_producer.get_context()
        collector_for_expected = _ExpectedPacketCollector(context)
        collector_for_actual = _ActualPacketCollector(context)
        # noinspection PyArgumentList
        data = self._data_producer(addr)
        if data:
            self._analyzer.decode_on(collector_for_expected, unhex(data))
        else:
            self._analyzer.create(collector_for_expected)
        self._analyzer.decode_on(collector_for_actual, actual_data)
        return list(collector_for_expected.get_packets()), list(collector_for_actual.get_packets())


class ProtocolTestCase(TestCase):

    _JSON_IMPORT_KEY = '__import__'

    def __init__(self, method_name: str) -> None:
        super().__init__(method_name)
        self.context = _ProtocolTestContext(self)

    def _get_file_name(self, kind: str, test_name: str, ext: str='json') -> str:
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), kind, test_name, ext)

    def _import_json(self, test_name_list: List[str]) -> Dict:
        data_json = {}
        for test_name in test_name_list:
            file_name = self._get_file_name('protocol_data', test_name)
            data_json.update(self._load_json(file_name))
        return data_json

    def _load_json(self, file_name: str) -> Dict:
        with open(file_name, 'r') as file:
            data_json = json.load(file)
            if self._JSON_IMPORT_KEY in data_json:
                data_json.update(self._import_json(data_json[self._JSON_IMPORT_KEY]))
                del data_json[self._JSON_IMPORT_KEY]
            return data_json

    def _load_data(self) -> _TestData:
        file_name = self._get_file_name('protocol_data', self._testMethodName)
        json_data = self._load_json(file_name) if os.path.exists(file_name) else {}
        return _TestData(self.context, json_data)

    def setUp(self) -> None:
        if self._testMethodName not in type(self).__dict__:
            self.skipTest('This test is defined in super class.')
        self.proxy = _ProtocolProxy()
        self.data = self._load_data()
        self._result_output = open(self._get_file_name('protocol_result', self._testMethodName, 'txt'), 'w')

    def tearDown(self) -> None:
        self._result_output.close()
        self.proxy.close()
        self.proxy = None
        self.data = None
        self.context = None

    def assert_that(self, actual: ReceivedData, expected: Dict[Address, List[EncodedData]]) -> None:
        try_action(lambda: self._assert_that(actual, expected), exception_factory=self.failureException)

    def _assert_that(self, actual: ReceivedData, expected: Dict[Address, List[EncodedData]]) -> None:
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
            print(get_packet_str(actual.packet), file=self._result_output)
            try_action(action, called_line=actual.called, packet_info=actual.packet_str)
        self.assertEqual(len(expected_packets), len(actual_packets),
                         'Following packets were left:\n'
                         '\n'.join(str(p) for p in actual_packets[len(expected_packets):]))
