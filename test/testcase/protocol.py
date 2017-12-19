import inspect
import json
from collections import defaultdict, deque
from os.path import dirname
from typing import NamedTuple as _NamedTuple
from unittest import TestCase

from pyminehub.mcpe.const import GameMode, Difficulty
from pyminehub.mcpe.network import MCPEHandler
from pyminehub.mcpe.world import WorldProxy
from pyminehub.mcpe.world.action import Action, ActionType
from pyminehub.mcpe.world.event import event_factory, EventType, Event
from pyminehub.network.address import Address
# noinspection PyProtectedMember
from pyminehub.raknet.server import _RakNetServerProtocol
from util.codec import *
from util.mock import MockEventLoop, MockTransport


class MockWorldProxy(WorldProxy):

    def __init__(self) -> None:
        self._event_queue = deque()  # type: Deque[Event]

    def perform(self, action: Action) -> None:
        if ActionType(action.id) == ActionType.LOGIN_PLAYER:
            self._event_queue.append(event_factory.create(EventType.PLAYER_LOGGED_IN, action.player_id))
            return
        if ActionType(action.id) == ActionType.UNKNOWN1:
            self._event_queue.append(event_factory.create(EventType.UNKNOWN1, action.player_id))
            return

    def next_event(self) -> Optional[Event]:
        try:
            return self._event_queue.popleft()
        except IndexError:
            return None

    def get_seed(self) -> int:
        return -1

    def get_game_mode(self) -> GameMode:
        return GameMode.SURVIVAL

    def get_difficulty(self) -> Difficulty:
        return Difficulty.NORMAL

    def get_rain_level(self) -> float:
        return 0.0

    def get_lightning_level(self) -> float:
        return 0.0

    def get_world_name(self) -> str:
        return 'PyMineHub Server'


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


class _TestDataProducer(Callable[[Address], str]):

    def __init__(self, test_case: TestCase, producer: Callable[[Address], str]) -> None:
        self.test_case = test_case
        self._producer = producer

    def __call__(self, addr: Address) -> str:
        return self._producer(addr)


class _TestData:

    def __init__(self, test_case: TestCase, json_dict: Dict) -> None:
        self._test_case = test_case
        self._json_dict = json_dict

    def that_is(self, name: str) -> _TestDataProducer:
        def producer(addr: Address) -> str:
            return self._json_dict[name]['client']['{}:{}'.format(*addr)].pop(0)
        return _TestDataProducer(self._test_case, producer)

    def that_is_response_of(self, name: str) -> _TestDataProducer:
        def producer(addr: Address) -> str:
            return self._json_dict[name]['server']['{}:{}'.format(*addr)].pop(0)
        return _TestDataProducer(self._test_case, producer)


DecodingInfo = _NamedTuple('PacketInfo', [
    ('packet', ValueObject),
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

    def replace_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        raise NotImplementedError()


class _ActualContext(_TestContext):

    def __init__(self, dynamic_values: Dict[str, Any]) -> None:
        self._dynamic_values = dynamic_values

    def get_name(self) -> str:
        return 'actual'

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        self._dynamic_values.update(dynamic_values)

    def replace_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        return packet


class _ExpectedContext(_TestContext):

    def get_name(self) -> str:
        return 'expected'

    def dynamic_value_found(self, dynamic_values: Dict[str, Any]) -> None:
        pass

    def replace_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)


class _PacketReplacer(PacketVisitor):

    def __init__(self, test_case: TestCase) -> None:
        self._test_case = test_case
        self._data = b''  # type: bytes

    def get_data(self) -> bytes:
        return self._data

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        self._test_case.assertEqual(expected, actual, message + '\n  when replacing')

    def assert_equal_for_encoding(self, expected: T, actual: T, message: str= '') -> None:
        pass

    def visit_after_decoding(
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs) -> ValueObject:
        # noinspection PyProtectedMember
        return packet._replace(**kwargs)

    def visit_after_encoding(self, packet: ValueObject, data: bytes, packet_str: str, called: str) -> None:
        self._data = data


class _PacketCollector(PacketVisitor):

    _PAYLOAD_MASK = {'payload': '[mask]'}

    def __init__(self, test_case: TestCase, context: _TestContext) -> None:
        self._test_case = test_case
        self._context = context
        self._packets = []

    def get_packets(self) -> Tuple[ValueObject, ...]:
        return tuple(reversed(self._packets))

    def assert_equal_for_decoding(self, expected: T, actual: T, message: str= '') -> None:
        self._test_case.assertEqual(
            expected, actual, message + '\n  when decoding {} data'.format(self._context.get_name()))

    def _replace_dynamic_values(self, packet: ValueObject, kwargs: Dict[str, Any]) -> ValueObject:
        dynamic_args = dict((key, value) for key, value in kwargs.items() if value is DYNAMIC)
        dynamic_values = dict((key, getattr(packet, key)) for key, value in dynamic_args.items())
        self._context.dynamic_value_found(dynamic_values)
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
            self, data: bytes, packet_id: ValueType, packet: ValueObject, packet_str: str, called: str, **kwargs) -> ValueObject:
        """Collect packets whose attributes is replaced with kwargs."""
        tmp_packet = self._replace_dynamic_values(packet, kwargs)
        tmp_packet = self._replace_payload(tmp_packet)
        tmp_packet = self._context.replace_values(tmp_packet, kwargs)
        self._packets.append(DecodingInfo(tmp_packet, data, called, '  ' + packet_str))
        return packet


class EncodedData:

    def __init__(self, data_producer: _TestDataProducer) -> None:
        """Encoded data validator.

        :param data_producer: data that decode to packet
        """
        self._data_producer = data_producer
        self._analyzer = None
        self._dynamic_values = {}  # type: Dict[str, Any]

    def get_dynamic_values(self) -> Dict[str, Any]:
        return self._dynamic_values

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    def __call__(self, addr: Address) -> str:
        def action():
            self._analyzer.decode_on(visitor, unhex(self._data_producer(addr)))
            self._analyzer.encode_on(visitor)
        test_case = self._data_producer.test_case
        visitor = _PacketReplacer(test_case)
        try_action(action, exception_factory=test_case.failureException)
        return visitor.get_data().hex()

    def collect_packet(self, actual_data: bytes, addr: Address) -> Tuple[List[ValueObject], List[ValueObject]]:
        test_case = self._data_producer.test_case
        collector_for_expected = _PacketCollector(test_case, _ExpectedContext())
        collector_for_actual = _PacketCollector(test_case, _ActualContext(self._dynamic_values))
        self._analyzer.decode_on(collector_for_expected, unhex(self._data_producer(addr)))
        self._analyzer.decode_on(collector_for_actual, actual_data)
        return list(collector_for_expected.get_packets()), list(collector_for_actual.get_packets())


class ProtocolTestCase(TestCase):

    _JSON_IMPORT_KEY = '__import__'

    def __init__(self, method_name: str) -> None:
        super().__init__(method_name)
        self.values = {}  # type: Dict[str, Any]

    def _get_file_name(self, test_name: str) -> str:
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), 'protocol_data', test_name, 'json')

    def _import_json(self, test_name_list: List[str]) -> Dict:
        data_json = {}
        for test_name in test_name_list:
            with open(self._get_file_name(test_name), 'r') as file:
                data_json.update(json.load(file))
        return data_json

    def setUp(self) -> None:
        if self._testMethodName not in type(self).__dict__:
            self.skipTest('This test is defined in super class.')
        self.proxy = _ProtocolProxy()
        with open(self._get_file_name(self._testMethodName), 'r') as file:
            data_json = json.load(file)
            if self._JSON_IMPORT_KEY in data_json:
                data_json.update(self._import_json(data_json[self._JSON_IMPORT_KEY]))
                del data_json[self._JSON_IMPORT_KEY]
            self.data = _TestData(self, data_json)

    def tearDown(self) -> None:
        self.proxy = None
        self.data = None

    def assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        try_action(lambda: self._assert_that(actual, expected), exception_factory=self.failureException)

    def _assert_that(self, actual: Dict[Address, List[bytes]], expected: Dict[Address, List[EncodedData]]) -> None:
        self.assertEqual(set(expected.keys()), set(actual.keys()),
                         'Clients specified by the address did not receive packets.')
        for addr in expected:
            expected_data_list = expected[addr]
            actual_data_list = actual[addr]
            self.assertEqual(
                len(expected_data_list), len(actual_data_list),
                '\n'.join(list(data.hex() for data in actual_data_list)))
            for expected_data in expected_data_list:
                self._assert_equal(actual_data_list.pop(0), expected_data, addr)

    def _assert_equal(self, actual: bytes, expected: EncodedData, addr: Address) -> None:
        expected_packets, actual_packets = expected.collect_packet(actual, addr)
        self.values.update(expected.get_dynamic_values())
        self.assertEqual(len(expected_packets), len(actual_packets))
        for expected, actual in zip(expected_packets, actual_packets):
            def action():
                self.assertEqual(expected.packet, actual.packet, "Actual data is '{}'".format(actual.data.hex()))
            try_action(action, called_line=actual.called, packet_info=actual.packet_str)
