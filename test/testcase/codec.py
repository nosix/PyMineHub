import inspect
import logging
from binascii import unhexlify as unhex
from os.path import dirname
from unittest import TestCase

from pyminehub import config
from util.codec import *

_logger = logging.getLogger(__name__)


def interrupt_for_pycharm(exc: Exception, called, packet_info: str=None) -> None:
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

    def __init__(self, exc: Exception, tb: traceback, message: str) -> None:
        super().__init__(message)
        self.exc = exc
        self.tb = tb


class CodecTestCase(TestCase):

    def __init__(self, method_name) -> None:
        super().__init__(method_name)
        self._bytes_mask_threshold = 16

    def set_bytes_mask_threshold(self, threshold: Optional[int]) -> None:
        self._bytes_mask_threshold = threshold

    def get_bytes_mask_threshold(self) -> Optional[int]:
        return self._bytes_mask_threshold

    def get_file_name(self, kind: str, ext='txt') -> str:
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), kind, self._testMethodName, ext)

    def setUp(self) -> None:
        _logger.setLevel(logging.INFO)
        self._file_handler = logging.FileHandler(self.get_file_name('codec_result'), 'w')
        _logger.addHandler(self._file_handler)
        config.reset()

    def tearDown(self) -> None:
        _logger.removeHandler(self._file_handler)
        self._file_handler.close()


class PacketAssertion(PacketVisitor):

    def __init__(self, test_case: CodecTestCase) -> None:
        self._test_case = test_case

    def get_bytes_mask_threshold(self) -> Optional[int]:
        return self._test_case.get_bytes_mask_threshold()

    def get_log_function(self) -> Callable[..., None]:
        return _logger.info

    def visit_decode_capsules(self, data: bytes, payload_length: int) -> None:
        self._test_case.assertEqual(len(data), payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    # noinspection PyMethodOverriding
    def visit_decode_task(
            self, packet_id_cls: PacketID, packet: Packet, data: bytes,
            context: PacketCodecContext, packet_id: PacketID, children_num: Optional[int]=None) -> None:
        self._test_case.assertEqual(packet_id, packet_id_cls(packet.id), packet)
        if packet_id_cls != CapsuleID:
            self._test_case.assertEqual(len(data), context.length)
        if children_num is not None:
            self._test_case.assertEqual(children_num, len(packet.payloads))

    def visit_encode_task(
            self, original_data: bytes, encoded_data: bytes, packet_info: str) -> None:
        self._test_case.assertEqual(original_data.hex(), encoded_data.hex(), packet_info)

    def try_action(
            self, action_of_raising_exception: Callable[[], None],
            called_line: Optional[str]=None, packet_info: Optional[str]=None) -> None:
        try:
            return action_of_raising_exception()
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise _WrappedException(e.exc, e.tb, message) from None
        except Exception as e:
            interrupt_for_pycharm(e, called_line, packet_info)
            message = '{} occurred while testing\n{}'.format(repr(e), called_line, packet_info)
            raise _WrappedException(e, sys.exc_info()[2], message) from None


class EncodedData:

    def __init__(self, data: str) -> None:
        """Encoded data validator.

        :param data: data that decode to packet
        """
        self._data = unhex(data)
        self._analyzer = None

    def is_(self, analyzer: PacketAnalyzer):
        self._analyzer = analyzer
        return self

    @staticmethod
    def _try_child_assertion(test_case: CodecTestCase, assertion_method: Callable[..., None], *args) -> None:
        try:
            assertion_method(*args)
        except _WrappedException as e:
            message = '{}'.format(e.args[0])
            raise test_case.failureException(message).with_traceback(e.tb) from None
        except Exception as e:
            interrupt_for_pycharm(e, None)
            raise e

    def is_correct_on(self, test_case: CodecTestCase, and_verified_with_encoded_data=False) -> None:
        assertion = PacketAssertion(test_case)
        self._try_child_assertion(test_case, self._analyzer.decode_on, assertion, self._data)
        if and_verified_with_encoded_data:
            self._try_child_assertion(test_case, self._analyzer.encode_on, assertion)
        else:
            self._analyzer.print_packet(assertion)


class EncodedDataInFile(EncodedData):

    def __init__(self, test_case: CodecTestCase) -> None:
        """Encoded data validator.

        Data is read from the file '{test_case_module_dir}/codec_data/{test_name}.txt'
        """
        with open(test_case.get_file_name('codec_data'), 'r') as file:
            data = ''.join(file.readlines())
        super().__init__(data)
