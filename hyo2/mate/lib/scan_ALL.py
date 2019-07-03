from hyo2.mate.lib.scan import *
#from pyall import *
from datetime import *
import struct


class ScanALL(Scan):
    '''scan an ALL file and provide some indicators of the contents'''
    _header_fmt = '<LBBHLLHH'
    _header_len = struct.calcsize(_header_fmt)
    _header_unpack = struct.Struct(_header_fmt).unpack_from
    _d1_data_fmt = '<2H6L5bB'
    _d1_data_len = struct.calcsize(_d1_data_fmt)
    _d1_data_unpack = struct.Struct(_d1_data_fmt).unpack_from
    _dh_data_fmt = '<lB'
    _dh_data_len = struct.calcsize(_dh_data_fmt)
    _dh_data_unpack = struct.Struct(_dh_data_fmt).unpack_from

    def __init__(self, file_path):
        Scan.__init__(self, file_path)
        self.reader = open(self.file_path, 'rb')

    # the source code of _more_data() and _read_header()
    # are copied from pyall.py
    def _more_data(self):
        '''report how many more bytes there are to read from the file'''
        return self.file_size - self.reader.tell()

    # added 'sequential counter' and 'serial number' as a part of the header
    # and changed date/time to time-stamp
    # this is to improve the performance
    def _read_header(self):
        '''read the common header for any datagram'''
        # initialize the reader
        try:
            curr = self.reader.tell()
            data = self.reader.read(self._header_len)
            s = self._header_unpack(data)

            numberOfBytes = s[0]
            STX = s[1]
            typeOfDatagram = chr(s[2])
            EMModel = s[3]
            RecordDate = s[4]
            RecordTime = float(s[5]/1000.0)
            Counter = s[6]
            SerialNumber = s[7]
            timeStamp = (datetime.strptime(str(RecordDate), '%Y%m%d')
                         + timedelta(0, RecordTime)
                         - datetime(1970, 1, 1)).total_seconds()

            # now reset file pointer
            # self.reader.seek(curr, 0)

            # we need to add 4 bytes as the message does not contain
            # the 4 bytes used to hold the size of the message
            # trap corrupt datagrams at the end of a file.
            # We see this in EM2040 systems.
            if (curr + numberOfBytes + 4) > self.file_size:
                numberOfBytes = self.file_size - curr - 4
                typeOfDatagram = 'XXX'
            return (numberOfBytes + 4, STX, typeOfDatagram,
                    EMModel, timeStamp, Counter, SerialNumber, curr)
        except struct.error:
            return (0, 0, 0, 0, 0, 0, 0, curr)

    def get_size_n_pings(self, pings):
        '''
        return bytes in the file which containg specified
        number of pings
        '''
        c_bytes = 0
        result = {}
        self.reader.seek(0, 0)
        while self._more_data():
            # read datagram header
            num_bytes, stx, dg_type, \
                em_model, unix_time, _counter, serial_number, _curr = \
                self._read_header()
            self.reader.seek(_curr + num_bytes, 0)
            c_bytes += num_bytes
            if dg_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y']:
                if dg_type not in result.keys():
                    result[dg_type] = {
                        'seqNo': _counter,
                        'count': 0,
                    }
                if _counter > result[dg_type]['seqNo']:
                    result[dg_type]['count'] += 1
                    if result[dg_type]['count'] > pings:
                        break
                result[dg_type]['seqNo'] = _counter
        return c_bytes

    def scan_datagram(self):
        '''scan data to extract basic information for each type of datagram'''

        self.scan_result = {}
        self.reader.seek(0, 0)
        while self._more_data():
            # update progress
            self.progress = 1 - self._more_data() // self.file_size

            # read datagram header
            num_bytes, stx, dg_type, \
                em_model, time_stamp, _counter, serial_number, _curr = \
                self._read_header()

            if dg_type not in self.scan_result.keys():
                self.scan_result[dg_type] = copy(self.default_info)
                self.scan_result[dg_type]['_seqNo'] = None

            # save datagram info
            self.scan_result[dg_type]['byteCount'] += num_bytes
            self.scan_result[dg_type]['recordCount'] += 1
            if self.scan_result[dg_type]['startTime'] is None:
                self.scan_result[dg_type]['startTime'] = time_stamp
            self.scan_result[dg_type]['stopTime'] = time_stamp
            if dg_type == 'I':
                # self.reader.seek(_curr + self._header_len, 0)
                ascii_bytes = num_bytes - self._header_len - 2
                data = self.reader.read(2 + ascii_bytes)
                parameters = {}
                for p in data[2:].decode('utf-8', errors="ignore").split(","):
                    parts = p.split('=')
                    if len(parts) > 1:
                        parameters[parts[0]] = parts[1].strip()
                if self.scan_result[dg_type]['other'] is None:
                    self.scan_result[dg_type]['other'] = parameters
            elif dg_type == '1':
                # self.reader.seek(_curr + self._header_len, 0)
                data = self.reader.read(self._d1_data_len)
                s = self._d1_data_unpack(data)
                self.scan_result[dg_type]['other'] = s[-5:]
            elif dg_type == 'h':
                # self.reader.seek(_curr + self._header_len, 0)
                data = self.reader.read(self._dh_data_len)
                s = self._dh_data_unpack(data)
                self.scan_result[dg_type]['other'] = s[1]
            elif dg_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y']:
                this_count = _counter
                last_count = self.scan_result[dg_type]['_seqNo']
                if last_count is None:
                    last_count = this_count
                if this_count - last_count >= 1:
                    self.scan_result[dg_type]['missedPings'] += \
                        this_count - last_count - 1
                    self.scan_result[dg_type]['pingCount'] += 1
                '''
                elif this_count - last_count < 0:
                    # in case Counter has rolled over
                    self.scan_result[dg_type]['missedPings'] += \
                        65535 - last_count + this_count
                    self.scan_result[dg_type]['pingCount'] += 1
                '''
                self.scan_result[dg_type]['_seqNo'] = \
                    this_count
            self.reader.seek(_curr + num_bytes, 0)
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
            dt = datetime.utcfromtimestamp(rec['startTime']).strftime('%Y%m%d')
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
                      for i in ['A', 'P', 'D', 'X', 'F', 'f', 'N'])
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
        if result1 == A_FULL and part4:
            return A_FULL
        if result1 == A_NONE and not part4:
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

    def is_missing_pings_tolerable(self, thresh=1.0):
        '''
        check for the number of missing pings in all multibeam
        data datagrams (D or X, F or f or N, S or Y)
        (allow the difference <= 1%)
        return: True/False
        '''
        for d_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y']:
            if d_type in self.scan_result.keys():
                rec = self.scan_result[d_type]
                if rec['pingCount'] == 0:
                    continue
                if rec['missedPings'] * 100.0 / rec['pingCount'] > thresh:
                    return False
        return True

    def has_minimum_pings(self, thresh=10):
        '''
        check if we have minimum number of requied pings in all multibeam
        data datagrams (D or X, F or f or N, S or Y)
        (minimum number is 10)
        return: True/False
        '''
        for d_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y']:
            if d_type in self.scan_result.keys():
                rec = self.scan_result[d_type]
                if rec['pingCount'] < thresh:
                    return False
        return True

    def ellipsoid_height_availability(self):
        '''
        check the presence of the datagrams h and
        type of nav string in datagram 1 (NMEG GGK)
        return: True/False
        '''
        rec = self.get_datagram_info('h')
        if rec is not None:
            return rec['other'] == 0
        return False

    def PU_status(self):
        '''
        check the status of all sensor in the datagrams 1
        type of nav string in datagram 1 (NMEG GGK)
        return: 'Fail'/'Pass'
        '''
        rec = self.get_datagram_info('1')
        if rec is not None:
            if all(1 for i in rec['other']):
                return A_PASS
        return A_FAIL
