import copy
import logging

from hyo2.mate.lib.scan_utils import get_scan, get_check, is_check_supported

logger = logging.getLogger(__name__)


class CheckRunner:
    """ The `CheckRunner` coordinates the execution of multiple checks based
    on a given QC JSON based definition.

    This class is strongly aligned towards supporting Scan checks. These checks
    work by first loading the metadata/header, then performing multiple checks
    on the loaded data. This check runner therefore performs checks by
    iterating over files, and performing multiple checks on each before moving
    to the next file.
    """

    def __init__(self, checks_def: list):
        """ `CheckRunner` constructor

        Args:
            checks_def (dict): definition of checks. This should conform to
                the checks block of the QC JSON schema.
        """
        self._input = checks_def
        # The check runner output will based on its input but add new content
        # based on check execution and results. Clone the input to use as the
        # basis of the output.
        self._output = copy.deepcopy(self._input)

    def initialize(self):
        """ Performs necessary preprocessing of the input before check
        execution can begin. This consists of remapping the input from a list
        of checks with files to a list of files with checks.
        """
        filechecks = {}
        for check in self._input:
            checkid = check['info']['id']
            checkversion = check['info']['version']
            if not is_check_supported(checkid, checkversion):
                # It's expected the QC JSON definition could include other
                # checks not supported by this application. Ignore these
                # checks.
                logger.warning(
                    "Check {} was ignored as it is not supported"
                    .format(check['id']))
                continue
            inputs = check['inputs']
            for input in inputs['files']:
                filename = input['path']

                if filename in filechecks:
                    checklistforfile = filechecks[filename]
                    checklistforfile.append(check)
                else:
                    checklistforfile = []
                    checklistforfile.append(check)
                    filechecks[filename] = checklistforfile

        self._file_checks = filechecks

    def run_checks():
        # TODO
        pass
