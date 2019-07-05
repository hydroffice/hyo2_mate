import unittest
import os
import pytest
import time
from hyo2.mate.lib.scan_utils import get_scan

TEST_FILE1 = "0200_MBES_EM122_20150203_010431_Supporter_GA4430.all"
TEST_FILE = "0243_P007_MBES_EM122_20150207_044356_Supporter_GA4430.all"


class TestMateScan(unittest.TestCase):

    def setUp(self):
        self.test_file = os.path.abspath(os.path.join(
                                         os.path.dirname(__file__),
                                         "test_data", TEST_FILE))

    def test_get_scan_all(self):
        _, extension = os.path.splitext(self.test_file)
        extension = extension[1:]  # remove the `.` char from extension
        scan = get_scan(self.test_file, extension)
        self.assertEqual(type(scan).__name__, 'ScanALL')

    def test_get_scan_unsupported(self):
        with pytest.raises(NotImplementedError):
            # following fn should raise a `NotImplementedError` when called
            get_scan('doesnotexist.something', 'unsupported_type')


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMateScan))
    return s
