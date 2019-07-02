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
            # update progress
            self.progress = 1 - self.reader.moreData() // self.file_size

            # read datagram header
            number_bytes, stx, datagram_type, \
                em_model, record_data, record_time = \
                self.reader.readDatagramHeader()
            time_stamp = to_timestamp(to_DateTime(record_data, record_time))

            # read datagram
            datagram_type, datagram = self.reader.readDatagram()
            '''
            raw_bytes = self.reader.readDatagramBytes(datagram.offset,
                                                      datagram.numberOfBytes)
            '''
            # datagram_name = self.reader.getDatagramName(datagram_type)
            if datagram_type not in self.scan_result.keys():
                self.scan_result[datagram_type] = copy(self.default_info)
                self.scan_result[datagram_type]['_seqNo'] = None

            # save datagram info
            self.scan_result[datagram_type]['byteCount'] += \
                datagram.numberOfBytes
            self.scan_result[datagram_type]['recordCount'] += 1
            if self.scan_result[datagram_type]['startTime'] is None:
                self.scan_result[datagram_type]['startTime'] = time_stamp
            self.scan_result[datagram_type]['stopTime'] = time_stamp
            if datagram_type in ['I', 'i']:
                datagram.read()
                p = datagram.installationParameters
                if self.scan_result[datagram_type]['other'] is None:
                    self.scan_result[datagram_type]['other'] = p
            elif not datagram.__class__.__name__ == 'UNKNOWN_RECORD':
                datagram.read()
                if hasattr(datagram, 'PingCounter'):
                    this_count = datagram.PingCounter
                if hasattr(datagram, 'Counter'):
                    this_count = datagram.Counter
                else:
                    this_count = None
                if this_count is not None:
                    last_count = self.scan_result[datagram_type]['_seqNo']
                    if last_count is None:
                        last_count = this_count
                    if this_count - last_count >= 1:
                        self.scan_result[datagram_type]['missedPings'] += \
                            this_count - last_count - 1
                        self.scan_result[datagram_type]['pingCount'] += 1
                    elif this_count - last_count < 0:
                        # in case PingCounter rolled over
                        self.scan_result[datagram_type]['missedPings'] += \
                            65535 - last_count + this_count
                        self.scan_result[datagram_type]['pingCount'] += 1
                    self.scan_result[datagram_type]['_seqNo'] = \
                        this_count
        return

    def is_filename_changed(self):
        '''
        check if the filename is different from what recorded
        in the datagram
        '''
        rfn = None
        rec = self.get_datagram_info('I')
        if rec is not None and 'RFN' in rec['other'].keys():
            rfn = rec['other']['RFN']
        return os.path.basename(self.file_path) != rfn

    def is_date_match(self):
        '''
        compare the date as in the datagram I and the date as written
        in the filename recorded in the datagram I
        return: True/False
        '''
        dt = 'unknown'
        rec = self.get_datagram_info('I')
        if rec is not None:
            if 'RFN' in rec['other'].keys():
                dt = rec['other']['RFN'].split('_')[1]
        return dt in os.path.basename(self.file_path)

    def bathymetry_availability(self):
        '''
        check the presence of all required datagrams for bathymetry processing
        (I, R, D or X, A, n, P, h, F or f or N, G, U)
        return: 'None'/'Partial'/'Full'
        '''
        presence = self.scan_result.keys()
        part1 = all(i in presence for i in ['I', 'R', 'A', 'n', 'P', 'h',
                                            'G', 'U'])
        part2 = any(i in presence for i in ['D', 'X'])
        part3 = any(i in presence for i in ['F', 'f', 'N'])
        if part1 and part2 and part3:
            return A_FULL
        partial = any(i in presence
                      for i in ['I', 'R', 'A', 'n', 'P', 'h', 'G', 'U',
                                'D', 'X', 'F', 'f', 'N'])
        if partial:
            return A_PARTIAL
        return A_NONE

    def backscatter_availability(self):
        '''
        check the presence of all required datagrams for backscatter processing
        (I, R, D or X, A, n, P, h, F or f or N, G, U, S or Y)
        return: 'None'/'Partial'/'Full'
        '''
        presence = self.scan_result.keys()
        result1 = self.bathymetry_availability()
        part4 = any(i in presence for i in ['S', 'Y'])
        if result1 == 'Full' and part4:
            return A_FULL
        if result1 == 'None' and not part4:
            return A_NONE
        return A_PARTIAL

    def ray_tracing_availability(self):
        '''
        check the presence of required datagrams for ray tracing
        (I, R, A, n, P, F or f or N, G, U)
        return: True/False
        '''
        presence = self.scan_result.keys()
        part0 = all(i in presence for i in ['I', 'R', 'A', 'n', 'P',
                                            'G', 'U'])
        part3 = any(i in presence for i in ['F', 'f', 'N'])
        return part0 and part3

    def ellipsoid_height_availability(self):
        '''
        check the presence of the datagrams h and
        type of nav string in datagram 1 (NMEG GGK)
        return: True/False
        '''
        presence = self.scan_result.keys()
        check0 = all(i in presence for i in ['1', 'h'])
        # TODO
        return False

    def PU_status(self):
        '''
        check the status of all sensor in the datagrams 1
        type of nav string in datagram 1 (NMEG GGK)
        return: 'Fail'/'Pass'
        '''
        rec = self.get_datagram_info('1')
        # TODO
        return A_FAIL

    def is_date_match(self):
        '''
        compare the date as in the datagram I and the date as written
        in the filename recorded in the datagram I
        return: True/False
        '''
        dt = 'unknown'
        rec = self.get_datagram_info('I')
        if rec is not None:
            if 'RFN' in rec['other'].keys():
                dt = rec['other']['RFN'].split('_')[1]
        return dt in os.path.basename(self.file_path)
