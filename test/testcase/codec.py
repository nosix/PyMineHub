import inspect
import logging
from os.path import dirname
from unittest import TestCase

from pyminehub import config
from util.codec import *
from util.exception import try_action

_logger = logging.getLogger(__name__)


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

    def visit_decode_capsules(self, data: bytes, decoded_payload_length: int) -> None:
        self._test_case.assertEqual(
            len(data), decoded_payload_length, 'Capsule may be missing with "{}"'.format(data.hex()))

    # noinspection PyMethodOverriding
    def visit_decode_task(self, packet_id_cls: PacketID, packet: Packet, data: bytes, called: str, packet_str: str,
                          context: PacketCodecContext, children_num: int, packet_id: PacketID) -> Packet:
        self._test_case.assertEqual(packet_id, packet_id_cls(packet.id), packet)
        if packet_id_cls != CapsuleID:
            self._test_case.assertEqual(len(data), context.length)
        if hasattr(packet, 'payloads'):
            self._test_case.assertEqual(children_num, len(packet.payloads))
        return packet

    def visit_encode_task(self, original_data: bytes, encoded_data: bytes, called: str, packet_str: str) -> None:
        packet_info = '\n{}\n  {}'.format(called, packet_str)
        self._test_case.assertEqual(original_data.hex(), encoded_data.hex(), packet_info)


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

    def is_correct_on(self, test_case: CodecTestCase, and_verified_with_encoded_data=False) -> None:
        assertion = PacketAssertion(test_case)
        try_action(lambda: self._analyzer.decode_on(assertion, self._data),
                   exception_factory=test_case.failureException)
        if and_verified_with_encoded_data:
            try_action(lambda: self._analyzer.encode_on(assertion),
                       exception_factory=test_case.failureException)
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
