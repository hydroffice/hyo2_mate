from hyo2.mate.lib.scan import Scan
from hyo2.mate.lib.scan_check import ScanCheck, FilenameChangedCheck, \
    DateChangedCheck, BathymetryAvailableCheck, BackscatterAvailableCheck, \
    RayTracingCheck, MinimumPingCheck, EllipsoidHeightAvailableCheck, \
    PuStatusCheck
from hyo2.mate.lib.scan_ALL import ScanALL


# List of all check implementations
all_checks = [
    BackscatterAvailableCheck,
    BathymetryAvailableCheck,
    DateChangedCheck,
    EllipsoidHeightAvailableCheck,
    FilenameChangedCheck,
    MinimumPingCheck,
    PuStatusCheck,
    RayTracingCheck,
]


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


def get_check(
    id: str, version: str, scan: Scan, params: list
) -> ScanCheck:
    """Factory method to return a new ScanCheck instance for the given id and
    version.

    Args:
        id (str): UUID for the check
        version (str): Version of the check to return
        scan (Scan): scan object that has parsed the file to be checked
        params (list): list of parameters that includes values needed for
            checks.

    Returns:
        New `ScanCheck` instance

    Raises:
        NotImplementedError: if check with `id` and `version` is not found
    """
    for check in all_checks:
        if id == check.id and version == check.version:
            return check(scan, params)

    raise NotImplementedError(
        "Check with id {} and version {} could not be found".format(
            id, version
        ))


def is_check_supported(id: str, version: str) -> bool:
    """ Indicates if the application supports this type of check.

    Args:
        id (str): UUID for the check
        version (str): Version of the check

    Returns:
        True if the check is supported (eg; it exists), otherwise false.
    """
    for check in all_checks:
        if id == check.id and version == check.version:
            return True
    return False
