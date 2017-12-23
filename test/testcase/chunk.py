import inspect
from binascii import unhexlify as unhex
from os.path import dirname
from unittest import TestCase


class ChunkTestCase(TestCase):

    def __init__(self, test_method_name) -> None:
        super().__init__(test_method_name)
        self.data = b''

    def get_file_name(self, kind: str, ext='txt') -> str:
        module_file_name = inspect.getmodule(self).__file__
        return '{}/{}/{}.{}'.format(dirname(module_file_name), kind, self._testMethodName, ext)

    def setUp(self):
        with open(self.get_file_name('chunk_data'), 'r') as file:
            self.data = unhex(''.join(file.readlines()))
