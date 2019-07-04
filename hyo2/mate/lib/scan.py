import os
from datetime import datetime
from copy import *

from scan_ALL import ScanALL

A_NONE = 'None'
A_PARTIAL = 'Partial'
A_FULL = 'Full'
A_FAIL = 'Fail'
A_PASS = 'Pass'


def get_scan(path: str, file_type: str) -> Scan:
    """Factory method to return a new Scan instance for the given file type.

    Args:
        path (str): Path to the file that will be read by the `Scan`
        file_type (str): Type of file to scan. Currently only `all` files are
            supported.

    Returns:
        New `Scan` instance

    Raises:
        NotImplementedError: if `file_type` is not supported
    """
    if (file_type.lower() == 'all'):
        return ScanALL(path)
    else:
        raise NotImplementedError(
            "File type {} is not supported".format(file_type))


class Scan:
    '''abstract class to scan a raw data file'''

    file_path = None
    file_size = None
    reader = None
    progress = 0       # completed percentage (0 - 100)
    scan_result = {}

    default_info = {
        'byteCount': 0,
        'recordCount': 0,
        'pingCount': 0,
        'missedPings': 0,
        'startTime': None,
        'stopTime': None,
        'other': None,
    }

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)

    def _time_str(self, unix_time):
        '''return time string in ISO format'''
        return datetime.utcfromtimestamp(unix_time)\
            .isoformat(timespec='milliseconds')

    def scan_datagram(self):
        '''
        scan data to extract basic information for each type of datagram
        and save to scan_result
        '''

    def get_datagram_info(self, datagram_type):
        '''return info about a specific type of datagrame'''
        if datagram_type in self.scan_result.keys():
            return self.scan_result[datagram_type]
        return None

    def get_total_pings(self, datagram_type=None):
        '''return the nuber of pings'''
        if datagram_type is not None:
            if datagram_type not in self.scan_result.keys():
                return 0
            return self.scan_result[datagram_type]['pingCount']
        total = 0
        for datagram_type in self.scan_result.keys():
            total += self.scan_result[datagram_type]['pingCount']
        return total

    def get_missed_pings(self, datagram_type=None):
        '''return the nuber of missed pings'''
        if datagram_type is not None:
            if datagram_type not in self.scan_result.keys():
                return 0
            return self.scan_result[datagram_type]['missedPings']
        total = 0
        for datagram_type in self.scan_result.keys():
            total += self.scan_result[datagram_type]['missedPings']
        return total

    def total_datagram_bytes(self):
        '''return number of bytes of all datagrams'''
        total_bytes = 0
        for datagram_type in self.scan_result.keys():
            total_bytes += self.scan_result[datagram_type]['byteCount']
        return total_bytes

    def is_size_matched(self):
        '''check if number of bytes of all datagrams is equal to file size'''
        return (self.total_datagram_bytes() == self.file_size)
