from hyo2.mate.lib.scan import Scan
from hyo2.mate.lib.scan_ALL import ScanALL


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
