from typing import List

from hyo2.mate.lib.scan import Scan
from hyo2.mate.lib.scan import A_NONE, A_PARTIAL, A_FULL, A_FAIL, A_PASS
from hyo2.qax.lib.qa_json import QaJsonParam, QaJsonOutputs


class ScanCheck:
    # list including default params to be used for the check
    # objects included in list will have a `name` and `value` attribute
    default_params = []

    def __init__(self, scan: Scan, params: List[QaJsonParam]):
        self.scan = scan
        self.params = params
        self._output = None  # QaJsonOutputs

    @property
    def output(self) -> QaJsonOutputs:
        """The output of the check. Will be empty until after `run_check` has
        been called.

        Returns:
            Dict that is structured according to the QA JSON schema.
        """
        return self._output

    def get_param(self, name: str) -> QaJsonParam:
        """ Gets a parameter based on the given name. Will return None if
        parameter does not exist.
        """
        match = next((p for p in self.params if p.name == name), None)
        return match

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

        msg = (
            "Filename does not match name embedded within file contents"
            if filename_changed
            else None
        )

        qa_pass = "no" if filename_changed else "yes"

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


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

        msg = (
            "File date does not match date embedded within file contents"
            if date_changed
            else None
        )

        qa_pass = "no" if date_changed else "yes"

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


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

        qa_pass = None
        msg = None
        if bathy_avail == A_FULL:
            qa_pass = "yes"
            msg = None
        elif bathy_avail == A_PARTIAL:
            qa_pass = "no"
            msg = "Only partial bathymetry is available"
        elif bathy_avail == A_NONE:
            qa_pass = "no"
            msg = "No bathymetry is available"
        else:
            qa_pass = "no"
            msg = "Bathymetry available flag {} is unknown".format(bathy_avail)

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


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

        qa_pass = None
        msg = None
        if bs_avail == A_FULL:
            qa_pass = "yes"
            msg = None
        elif bs_avail == A_PARTIAL:
            qa_pass = "no"
            msg = "Backscatter available"
        elif bs_avail == A_NONE:
            qa_pass = "no"
            msg = "Backscatter available"
        else:
            qa_pass = "no"
            msg = "Backscatter available flag {} is unknown".format(bs_avail)

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


class RayTracingCheck(ScanCheck):
    """Checks Ray Tracing data is available.
    """
    id = '5421f3f2-6e37-4740-bf83-488bebde49f4'
    name = "Ray Tracing Available"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        rt_avail = self.scan.ray_tracing_availability()

        msg = (
            None
            if rt_avail
            else "Ray tracing is not available"
        )

        qa_pass = "yes" if rt_avail else "no"

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


class MinimumPingCheck(ScanCheck):
    """Checks for minimum number of required pings in all multibeam datagrams.
    If the params list includes a `threshold` entry this will be used,
    otherwise the default of 10 will be applied.
    """
    id = 'd762fd79-75bc-4aff-a9d2-e0c36e744e17'
    name = "Minimum Ping count"
    version = '1'
    default_params = [
        QaJsonParam(name='threshold', value=20)
    ]

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        passed = None
        threshold_param = self.get_param('threshold')
        if threshold_param is not None:
            passed = self.scan.has_minimum_pings(threshold_param.value)
        else:
            passed = self.scan.has_minimum_pings()

        msg = (
            None
            if passed
            else (
                "Minimum ping count is less than threshold count of 10"
                if threshold_param is None
                else (
                    "Minimum ping count is less than threshold count of {}"
                    .format(threshold_param.value))
            )
        )

        qa_pass = "yes" if passed else "no"

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


class EllipsoidHeightAvailableCheck(ScanCheck):
    """Checks Ellipsoid Height is available.
    """
    id = 'bbce47c0-54c9-4c60-8de8-b174a8905091'
    name = "Ellipsoid Height Available"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        eh_avail = self.scan.ellipsoid_height_availability()

        msg = (
            None
            if rt_avail
            else "Ellipsoid height is not available"
        )

        qa_pass = "yes" if eh_avail else "no"

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )


class PuStatusCheck(ScanCheck):
    """Check the status of all sensor in the datagrams 1 type of nav string
    in datagram 1 (NMEG GGK)
    """
    id = '37b967ac-3e82-40f6-ba24-4badcf1317f3'
    name = "PU Status"
    version = '1'

    def __init__(self, scan: Scan, params):
        ScanCheck.__init__(self, scan, params)

    def run_check(self):
        pu_status = self.scan.PU_status()

        msg = None
        qa_pass = None
        if pu_status == A_PASS:
            qa_pass = "yes"
            msg = None
        elif pu_status == A_FAIL:
            qa_pass = "no"
            msg = None
        else:
            qa_pass = "no"
            msg = "PU Status flag {} is unknown".format(pu_status)

        self._output = QaJsonOutputs(
            execution=None,
            files=None,
            count=None,
            percentage=None,
            message=msg,
            qa_pass=qa_pass
        )
