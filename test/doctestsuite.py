import inspect
import runpy
import unittest
from os.path import dirname


class DocTestCase(unittest.TestCase):

    def test_doctest(self):
        module_file_name = inspect.getmodule(self).__file__
        test_dir = dirname(module_file_name)
        module_path = [
            'pyminehub/config',
            'pyminehub/binutil/converter',
            'pyminehub/binutil/composite',
            'pyminehub/value',
            'pyminehub/network/codec',
            'pyminehub/raknet/codec',
            'pyminehub/mcpe/value',
            'pyminehub/mcpe/network/codec/connection',
        ]
        for path in module_path:
            with self.subTest(module=path):
                result = runpy.run_path(
                    '{}/../src/{}.py'.format(test_dir, path), run_name='__main__')['doctest_result']
                self.assertEqual(0, result.failed, result)


if __name__ == '__main__':
    import unittest
    unittest.main()
