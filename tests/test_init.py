import unittest

from hyo2 import mate


class TestMateInit(unittest.TestCase):

    def test_has_version(self):

        self.assertIsNot(len(mate.__version__), 0)

    def test_is_version_more_than_0(self):
        self.assertGreaterEqual(int(mate.__version__.split('.')[0]), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMateInit))
    return s
