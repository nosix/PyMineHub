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
            'pyminehub/value',
            'pyminehub/binutil/converter',
            'pyminehub/binutil/composite',
            'pyminehub/network/codec',
            'pyminehub/raknet/codec',
            'pyminehub/mcpe/const',
            'pyminehub/mcpe/geometry',
            'pyminehub/mcpe/value',
            'pyminehub/mcpe/command/annotation',
            'pyminehub/mcpe/command/api',
            'pyminehub/mcpe/plugin/loader',
            'pyminehub/mcpe/world/item',
            'pyminehub/mcpe/world/block',
            'pyminehub/mcpe/network/codec/connection',
        ]
        for path in module_path:
            with self.subTest(module=path):
                result = runpy.run_path(
                    '{}/../src/{}.py'.format(test_dir, path), run_name='__main__')['doctest_result']
                self.assertEqual(0, result.failed, path)


if __name__ == '__main__':
    import unittest
    unittest.main()
