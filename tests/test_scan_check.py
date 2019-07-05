import unittest
import os
import time
import pytest
from hyo2.mate.lib.scan_utils import get_scan, get_check


TEST_FILE1 = "0200_MBES_EM122_20150203_010431_Supporter_GA4430.all"
TEST_FILE = "0243_P007_MBES_EM122_20150207_044356_Supporter_GA4430.all"


class TestMateScanCheck(unittest.TestCase):

    def setUp(self):
        self.test_file = os.path.abspath(os.path.join(
                                         os.path.dirname(__file__),
                                         "test_data", TEST_FILE))

    def test_get_check(self):
        scan = get_scan(self.test_file, 'all')

        # id and version for the filename changed check
        check_id = '7761e08b-1380-46fa-a7eb-f1f41db38541'
        check_version = '1'
        check_params = {}
        check = get_check(check_id, check_version, scan, check_params)

        self.assertEqual(type(check).__name__, 'FilenameChangedCheck')

    def test_get_check_bad_version(self):
        scan = get_scan(self.test_file, 'all')

        # id and version for the filename changed check
        check_id = '7761e08b-1380-46fa-a7eb-f1f41db38541'
        check_version = '-1'  # bad version
        check_params = {}
        with pytest.raises(NotImplementedError):
            check = get_check(check_id, check_version, scan, check_params)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMateScanCheck))
    return s
