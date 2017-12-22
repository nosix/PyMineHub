import runpy
import unittest


class DocTestCase(unittest.TestCase):

    def test_doctest(self):
        module_path = [
            'pyminehub/config',
            'pyminehub/binutil/converter',
            'pyminehub/value',
            'pyminehub/network/codec',
            'pyminehub/raknet/codec',
            'pyminehub/mcpe/network/codec/connection',
        ]
        for path in module_path:
            with self.subTest(module=path):
                result = runpy.run_path('../src/{}.py'.format(path), run_name='__main__')['doctest_result']
                self.assertEqual(0, result.failed, result)


if __name__ == '__main__':
    import unittest
    unittest.main()
