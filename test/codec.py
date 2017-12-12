import inspect
import logging
from binascii import unhexlify as unhex
from os.path import dirname
from unittest import TestCase

from pyminehub import config
from pyminehub.debug.codec import *
from pyminehub.mcpe.network.packet import ConnectionPacketID
from pyminehub.mcpe.network.packet import GamePacketID
from pyminehub.network.codec import PacketCodecContext
from pyminehub.network.packet import Packet
from pyminehub.raknet.encapsulation import CapsuleID
from pyminehub.raknet.packet import RakNetPacketID

_logger = logging.getLogger(__name__)


def interrupt_for_pycharm(exc: Exception, called, packet_info: str=None):
    if type(exc).__name__ == 'EqualsAssertionError':
        attrs = exc.__dict__
        if called is not None:
            if 'called' not in attrs:
                attrs['called'] = called
            if 'stack' not in attrs:
                attrs['stack'] = []
            if packet_info is not None:
                attrs['stack'].append(packet_info)
        else:
            messages = ['AssertionError occurred while testing', attrs['called'][:-1]]  # remove \n
            messages.extend(attrs['stack'])
            messages.append(attrs['msg'])
            attrs['msg'] = '\n'.join(messages)
        raise exc


class _WrappedException(Exception):

    def __init__(self, exc: Exception, tb: traceback, message: str):
        super().__init__(message)
        self.exc = exc
        self.tb = tb


class CodecTestCase(TestCase):

    def __init__(self, method_name):
        super().__init__(method_name)
        self._bytes_mask_enabled = True

    def enable_bytes_mask(self, value):
        self._bytes_mask_enabled = value

    def is_enabled_bytes_mask(self) -> bool:
        return self._bytes_mask_enabled

    def get_file_name(self, kind: str, ext='txt'):
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), kind, self._testMethodName, ext)

    def setUp(self):
        _logger.setLevel(logging.INFO)
        self._file_handler = logging.FileHandler(self.get_file_name('codec_result'), 'w')
        _logger.addHandler(self._file_handler)
        config.reset()

    def tearDown(self):
        _logger.removeHandler(self._file_handler)
        self._file_handler.close()


class PacketAssertion(PacketVisitor):

    def __init__(self, test_case: CodecTestCase) -> None:
        self._test_case = test_case

    def is_enabled_bytes_mask(self) -> bool:
        return self._test_case.is_enabled_bytes_mask()

    def get_log_function(self) -> Callable[..., None]:
        return _logger.info

    # noinspection PyMethodOverriding
    def visit_decode_raknet_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, packet_id: RakNetPacketID) -> None:
        self._test_case.assertEqual(packet_id, RakNetPacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)

    def visit_decode_capsules(self, data: bytes, payload_length: int) -> None:
        self._test_case.assertEqual(len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    # noinspection PyMethodOverriding
    def visit_decode_capsule_task(
            self, capsule: Packet, data: bytes, context: PacketCodecContext, capsule_id: CapsuleID) -> None:
        self._test_case.assertEqual(capsule_id, CapsuleID(capsule.id))

    # noinspection PyMethodOverriding
    def visit_decode_connection_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, packet_id: ConnectionPacketID) -> None:
        self._test_case.assertEqual(packet_id, ConnectionPacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)

    # noinspection PyMethodOverriding
    def visit_decode_batch_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext,
            expected_payloads_num: int, packet_id: ConnectionPacketID) -> None:
        self._test_case.assertEqual(packet_id, ConnectionPacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)
        self._test_case.assertEqual(expected_payloads_num, len(packet.payloads))

    # noinspection PyMethodOverriding
    def visit_decode_game_packet_task(
            self, packet: Packet, data: bytes, context: PacketCodecContext, packet_id: GamePacketID) -> None:
        self._test_case.assertEqual(packet_id, GamePacketID(packet.id), packet)
        self._test_case.assertEqual(len(data), context.length)

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        self._test_case.assertEqual(original_data.hex(), encoded_data.hex(), packet_info)

    def try_action(
            self, action_of_raising_exception: Callable[[], None],
            called_line: Optional[str]=None, message: Optional[str]=None) -> None:
        try:
            return action_of_raising_exception()
        except _WrappedException as e:
            exc_message = '{}'.format(e.args[0])
            raise _WrappedException(e.exc, e.tb, exc_message) from None
        except Exception as e:
            interrupt_for_pycharm(e, called_line, message)
            exc_message = '{} occurred while testing\n{}'.format(repr(e), called_line, message)
            raise _WrappedException(e, sys.exc_info()[2], exc_message) from None


class EncodedData:

    def __init__(self, data: str):
        """ Encoded data validator.

        :param data: data that decode to packet
        """
        self._data = unhex(data)
        self._analyzer = None

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    @staticmethod
    def _try_child_assertion(test_case: CodecTestCase, assertion_method: Callable[..., None], *args):
        try:
            assertion_method(*args)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise test_case.failureException(message).with_traceback(e.tb) from None
        except Exception as e:
            interrupt_for_pycharm(e, None)
            raise e

    def is_correct_on(self, test_case: CodecTestCase, and_verified_with_encoded_data=False):
        assertion = PacketAssertion(test_case)
        self._try_child_assertion(test_case, self._analyzer.decode_on, assertion, self._data)
        if and_verified_with_encoded_data:
            self._try_child_assertion(test_case, self._analyzer.encode_on, assertion)
        else:
            self._analyzer.print_packet(assertion)


class EncodedDataInFile(EncodedData):

    def __init__(self, test_case: CodecTestCase):
        """ Encoded data validator.

        Data is read from the file '{test_case_module_dir}/codec_data/{test_name}.txt'
        """
        with open(test_case.get_file_name('codec_data'), 'r') as file:
            data = ''.join(file.readlines())
        super().__init__(data)
