import unittest
import os
import time
from hyo2.mate.lib.scan_ALL import ScanALL

TEST_FILE = "0200_MBES_EM122_20150203_010431_Supporter_GA4430.all"


class TestMateScanALL(unittest.TestCase):

    def setUp(self):
        self.test_file = os.path.abspath(os.path.join(
                                         os.path.dirname(__file__),
                                         "test_data", TEST_FILE))
        self.test = ScanALL(self.test_file)
        self.test.scan_datagram()

    def test_time_str(self):
        return self.test._time_str(time.time())

    def test_get_datagram_info(self):
        self.test.get_datagram_info('D')

    def test_pings(self):
        self.test.get_total_pings('f')
        self.test.get_missed_pings('f')
        self.test.get_total_pings('-')
        self.test.get_missed_pings('-')
        self.test.get_total_pings()
        self.test.get_missed_pings()

    def test_is_size_matched(self):
        self.test.is_size_matched()

    def test_is_filename_changed(self):
        self.test.is_filename_changed()

    def test_bathymetry_availability(self):
        self.test.bathymetry_availability()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMateScanALL))
    return s
