from typing import List, Dict, NoReturn, Callable
from pathlib import Path

from hyo2.mate.lib.scan_utils import all_checks
from hyo2.mate.lib.check_runner import CheckRunner
from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from hyo2.qax.lib.qa_json import QaJsonRoot, QaJsonDataLevel, QaJsonCheck, \
    QaJsonFile, QaJsonInputs


class MateQaxPlugin(QaxCheckToolPlugin):

    # all Mate checks support the same file types
    supported_file_types = [
        QaxFileType(
            name="Kongsberg raw sonar files",
            extension="all",
            group="Raw Files",
            icon="kng.png"
        ),
        # QaxFileType(
        #     name="Kongsberg raw sonar files",
        #     extension="wcd",
        #     group="Raw Files",
        #     icon="kng.png"
        # )
    ]

    def __init__(self):
        super(MateQaxPlugin, self).__init__()
        # name of the check tool
        self.name = 'Mate'
        self._check_references = self._build_check_references()
        self.stopped = False
        self.check_runner = None

    def _build_check_references(self) -> List[QaxCheckReference]:
        data_level = "raw_data"
        check_refs = []
        for mate_check_class in all_checks:
            cr = QaxCheckReference(
                id=mate_check_class.id,
                name=mate_check_class.name,
                data_level=data_level,
                description=None,
                supported_file_types=MateQaxPlugin.supported_file_types,
                default_input_params=mate_check_class.default_params,
                version=mate_check_class.version,
            )
            check_refs.append(cr)
        return check_refs

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def __check_files_match(self, a: QaJsonInputs, b: QaJsonInputs) -> bool:
        """ Checks if the input files in a are the same as b. This is used
        to match the plugin's output with the QAJSON outputs that must be
        updated with the check results.
        """
        set_a = set([str(p.path) for p in a.files])
        set_b = set([str(p.path) for p in b.files])
        return set_a == set_b

    def run(
            self,
            qajson: QaJsonRoot,
            progress_callback: Callable = None
            ) -> NoReturn:
        self.stopped = False

        # Mate still works with QA JSON dicts, so use the qajson objects
        # to_dict function to generate it.
        rawdatachecks = qajson.qa.raw_data.to_dict()['checks']

        self.check_runner = CheckRunner(rawdatachecks)
        self.check_runner.initialize()

        # the check_runner callback accepts only a float, whereas the qax
        # qwax plugin check tool callback requires a referece to a check tool
        # AND a progress value. Hence this little mapping function,
        def pg_call(check_runner_progress):
            progress_callback(self, check_runner_progress)

        self.check_runner.run_checks(pg_call)

        # the checks runner produces an array containing a listof checks
        # each check being a dictionary. Deserialise these using the qa json
        # datalevel class
        out_dl = QaJsonDataLevel.from_dict(
            {'checks': self.check_runner.output})

        # now loop through all raw_data (Mate only does raw data) checks in
        # the qsjson and update the right checks with the check runner output
        for out_check in out_dl.checks:
            # find the check definition in the input qajson.
            # note: both check and id must match. The same check implmenetation
            # may be include twice but with diffferent names (this is
            # supported)
            in_check = next(
                (
                    c
                    for c in qajson.qa.raw_data.checks
                    if (
                        c.info.id == out_check.info.id and
                        c.info.name == out_check.info.name and
                        self.__check_files_match(c.inputs, out_check.inputs))
                ),
                None
            )
            if in_check is None:
                # this would indicate a check was run that was not included
                # in the input qajson. *Should never occur*
                raise RuntimeError(
                    "Check {} ({}) found in output that was not "
                    "present in input"
                    .format(out_check.info.name, out_check.info.id))
            # replace the input qajson check outputs with the output generated
            # by the check_runner
            in_check.outputs = out_check.outputs

    def stop(self):
        self.stopped = True
        if self.check_runner is not None:
            self.check_runner.stop()

    def update_qa_json_input_files(
            self, qa_json: QaJsonRoot, files: List[Path]) -> NoReturn:
        """ Updates qa_json to support the list of provided files. function
        defined in base class has been overwritten to support some Mate
        specifics in the way it supports multiple files.
        """
        # when this function has been called qa_json has been updated to
        # include the list of checks. While Mate will support processing of
        # multiple files within one QA JSON check definition, the QA JSON
        # schema doesn't support multiple outputs per check. To work around
        # this, this function take the specified checks, and adds one check
        # definition per file. Each Mate check is therefore run with a single
        # input file, but the same check is duplicated for each file passed in
        all_data_levels = [check_ref.data_level for check_ref in self.checks()]
        all_data_levels = list(set(all_data_levels))

        # build a list of mate checks in the qa_json for all the different data
        # levels (this really only needs to check the raw_data data level)
        all_mate_checks = []
        for dl in all_data_levels:
            dl_sp = getattr(qa_json.qa, dl)
            if dl_sp is None:
                continue
            for check in dl_sp.checks:
                if self.get_check_reference(check.info.id) is not None:
                    all_mate_checks.append(check)

        # now remove the current Mate definitions as we'll add these all back
        # in again for each input file.
        for mate_check in all_mate_checks:
            for dl in all_data_levels:
                dl_sp = getattr(qa_json.qa, dl)
                dl_sp.checks.remove(mate_check)

        for input_file in files:
            for mate_check in all_mate_checks:
                check_ref = self.get_check_reference(mate_check.info.id)
                if not check_ref.supports_file(input_file):
                    continue
                mate_check_clone = QaJsonCheck.from_dict(mate_check.to_dict())
                inputs = mate_check_clone.get_or_add_inputs()
                inputs.files.append(
                    QaJsonFile(path=str(input_file), description=None))
                # ** ASSUME ** mate checks only go in the raw_data data level
                qa_json.qa.raw_data.checks.append(mate_check_clone)
