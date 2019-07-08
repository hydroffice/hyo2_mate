from hyo2.mate.lib.scan import Scan
from hyo2.mate.lib.scan import A_NONE, A_PARTIAL, A_FULL, A_FAIL, A_PASS


class ScanCheck:

    def __init__(self, scan: Scan, params: dict):
        self.scan = scan
        self.params = params
        self._output = {}

    @property
    def output(self) -> dict:
        """The output of the check. Will be empty until after `run_check` has
        been called.

        Returns:
            Dict that is structured according to the QC JSON schema.
        """
        return self._output

    def run_check(self):
        """Executes the check. Specific logic is implemented in the child/
        concrete classes.

        Raises:
            NotImplementedError: If the `run_check` method has not been
                overwritten by the concrete implmenetation.
        """
        raise NotImplementedError("run_check must be overwritten")


class FilenameChangedCheck(ScanCheck):
    """Checks if the name of the file matches that recorded in the metadata/
    file header.
    """
    id = '7761e08b-1380-46fa-a7eb-f1f41db38541'
    name = "Filename checked"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        filename_changed = self.scan.is_filename_changed()

        # Currently limited by schema to output a percent. If the filename has
        # changed we'll put it in as 0 (fail), if it hasn't changed then we'll
        # say it's 100%
        self._output['percentage'] = 0 if filename_changed else 100


class DateChangedCheck(ScanCheck):
    """Checks if the date included in the filename matches that recorded in
    the metadata/file header.
    """
    id = '4a3f3371-3a21-44f2-93cf-d9ed19d0c002'
    name = "Date checked"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        date_changed = not self.scan.is_date_match()

        self._output['percentage'] = 0 if date_changed else 100


class BathymetryAvailableCheck(ScanCheck):
    """Checks bathymetry data is available.
    """
    id = '8c909ace-8759-4c2c-b86a-f76f888cd821'
    name = "Bathymetry Available"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        bathy_avail = self.scan.bathymetry_availability()

        if bathy_avail == A_FULL:
            self._output['percentage'] = 100
        elif bathy_avail == A_PARTIAL:
            self._output['percentage'] = 50
        elif bathy_avail == A_NONE:
            self._output['percentage'] = 0
        else:
            raise NotImplementedError(
                "Bathymetry available flag {} is unknown".format(bathy_avail))


class BackscatterAvailableCheck(ScanCheck):
    """Checks backscatter data is available.
    """
    id = 'bbce47c0-54c9-4c60-8de8-b174a8905091'
    name = "Backscatter Available"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        bs_avail = self.scan.backscatter_availability()

        if bs_avail == A_FULL:
            self._output['percentage'] = 100
        elif bs_avail == A_PARTIAL:
            self._output['percentage'] = 50
        elif bs_avail == A_NONE:
            self._output['percentage'] = 0
        else:
            raise NotImplementedError(
                "Backscatter available flag {} is unknown".format(bs_avail))
