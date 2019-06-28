import time
from copy import *


class Scan:
    '''abstract class to scan a raw data file'''

    file_path = None
    reader = None
    scan_result = {}

    default_info = {
        'recordCount': 0,
        'missingRecords': 0,
        'byteCount': 0,
        'startTime': None,
        'stopTime': None,
        'other': None,
    }

    def __init__(self, file_path):
        self.file_path = file_path

    def _time_str(self, unix_time):
        '''return time string in ISO format'''
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(unix_time))

    def scan_datagram(self):
        '''
        scan data to extract basic information for each type of datagram
        and save to scan_result
        '''
        return

    def get_datagram_info(self, datagram_type):
        '''return info about a specific type of datagrame'''
        if datagram_type in self.scan_result.keys():
            return self.scan_result[datagram_type]
        return None

    def is_record_missed(self, datagram_type=None):
        if datagram_type is not None:
            if datagram_type not in self.scan_result.keys():
                return True
            return self.scan_result[datagram_type]['missingRecords'] > 0
        for datagram_type in self.scan_result.keys():
            if self.scan_result[datagram_type]['missingRecords'] > 0:
                return True
        return False
