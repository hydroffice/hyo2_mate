from hyo2.mate.lib.scan import *
from pyall import *


class ScanALL(Scan):
    '''scan an ALL file and provide some indicators of the contents'''

    def scan_datagram(self):
        '''scan data to extract basic information for each type of datagram'''

        if len(self.scan_result) > 0:   # check if scan is already done
            return

        # initialize the reader
        if self.reader is None:
            self.reader = ALLReader(self.file_path)
        self.reader.rewind()

        while self.reader.moreData():
            number_bytes, stx, datagram_type, \
                em_model, record_data, record_time = \
                self.reader.readDatagramHeader()
            self.reader.fileptr.seek(number_bytes, 1)
            if datagram_type not in self.scan_result.keys():
                self.scan_result[datagram_type] = copy(self.default_info)
                self.scan_result[datagram_type]['_sequenceNo'] = 0

            self.scan_result[datagram_type]['recordCount'] += 1
            if self.scan_result[datagram_type]['startTime'] is None:
                self.scan_result[datagram_type]['startTime'] = \
                    to_timestamp(to_DateTime(record_data, record_time))
            self.scan_result[datagram_type]['stopTime'] = \
                to_timestamp(to_DateTime(record_data, record_time))
        return
