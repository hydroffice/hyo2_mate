from hyo2.mate.lib.scan import *
from pyall import *


class ScanALL(Scan):
    '''scan an ALL file and provide some indicators of the contents'''
    _header_fmt = '=LBBHLLH'
    _header_len = struct.calcsize(_header_fmt)
    _header_unpack = struct.Struct(_header_fmt).unpack_from
    _file_ptr = None

    # this is to improve the performance
    # the source code is copied from pyall.py
    # but added 'sequential counter' as a part of the header
    def _read_header(self):
        '''read the common header for any datagram'''
        try:
            curr = self._file_ptr.tell()
            data = self._file_ptr.read(self._header_len)
            s = self._header_unpack(data)

            numberOfBytes = s[0]
            STX = s[1]
            typeOfDatagram = chr(s[2])
            EMModel = s[3]
            RecordDate = s[4]
            RecordTime = float(s[5]/1000.0)
            Counter = s[6]

            # now reset file pointer
            self._file_ptr.seek(curr, 0)

            # we need to add 4 bytes as the message does not contain
            # the 4 bytes used to hold the size of the message
            # trap corrupt datagrams at the end of a file.
            # We see this in EM2040 systems.
            if (curr + numberOfBytes + 4) > self.file_size:
                numberOfBytes = self.file_size - curr - 4
                typeOfDatagram = 'XXX'
            return (numberOfBytes + 4, STX, typeOfDatagram,
                    EMModel, RecordDate, RecordTime, Counter, curr)
        except struct.error:
            return (0, 0, 0, 0, 0, 0, 0, curr)

    def scan_datagram(self):
        '''scan data to extract basic information for each type of datagram'''

        if len(self.scan_result) > 0:   # check if scan is already done
            return

        # initialize the reader
        if self.reader is None:
            self.reader = ALLReader(self.file_path)
            self._file_ptr = self.reader.fileptr
        self.reader.rewind()

        while self.reader.moreData():
            # update progress
            self.progress = 1 - self.reader.moreData() // self.file_size

            # read datagram header
            num_bytes, stx, dg_type, \
                em_model, record_date, record_time, _counter, _curr = \
                self._read_header()
            time_stamp = to_timestamp(to_DateTime(record_date, record_time))

            # read datagram
            # dg_type, datagram = self.reader.readDatagram()
            # datagram_name = self.reader.getDatagramName(dg_type)

            if dg_type not in self.scan_result.keys():
                self.scan_result[dg_type] = copy(self.default_info)
                self.scan_result[dg_type]['_seqNo'] = None

            # save datagram info
            self.scan_result[dg_type]['byteCount'] += num_bytes
            self.scan_result[dg_type]['recordCount'] += 1
            if self.scan_result[dg_type]['startTime'] is None:
                self.scan_result[dg_type]['startTime'] = time_stamp
            self.scan_result[dg_type]['stopTime'] = time_stamp
            if dg_type in ['I', 'i']:
                dg_type, datagram = self.reader.readDatagram()
                datagram.read()
                p = datagram.installationParameters
                if self.scan_result[dg_type]['other'] is None:
                    self.scan_result[dg_type]['other'] = p
            elif dg_type == '1':
                _data_fmt = '=3H6L5bB'
                _data_len = struct.calcsize(_data_fmt)
                _data_unpack = struct.Struct(_data_fmt).unpack_from
                self._file_ptr.seek(_curr + self._header_len, 0)
                data = self._file_ptr.read(_data_len)
                s = _data_unpack(data)
                self.scan_result[dg_type]['other'] = s[-5:]
            elif dg_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y', 'R']:
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
            self._file_ptr.seek(_curr + num_bytes, 0)
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
            dt = time.strftime("%Y%m%d", time.gmtime(rec['startTime']))
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

    def is_missing_pings_tolerable(self):
        '''
        check for the number of missing pings in all multibeam
        data datagrams (D or X, F or f or N, S or Y)
        (allow the difference <= 1%)
        return: True/False
        '''
        for d_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y', 'R']:
            if d_type in self.scan_result.keys():
                rec = self.scan_result[d_type]
                if rec['pingCount'] == 0:
                    continue
                if rec['missedPings'] * 100.0 / rec['pingCount'] > 1.0:
                    return False
        return True

    def has_minimum_pings(self):
        '''
        check if we have minimum number of requied pings in all multibeam
        data datagrams (D or X, F or f or N, S or Y)
        (minimum number is 10)
        return: True/False
        '''
        for d_type in ['D', 'X', 'F', 'f', 'N', 'S', 'Y']:
            if d_type in self.scan_result.keys():
                rec = self.scan_result[d_type]
                if rec['pingCount'] < 10:
                    return False
        return True

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
        if rec is not None:
            if all(1 for i in rec['other']):
                return A_PASS
        return A_FAIL
