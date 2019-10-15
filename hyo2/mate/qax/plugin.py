from typing import List, Dict, NoReturn, Callable

from hyo2.mate.lib.scan_utils import all_checks
from hyo2.mate.lib.check_runner import CheckRunner
from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from hyo2.qax.lib.qa_json import QaJsonRoot


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

        # todo: get output from checks and update qajson object

    def stop(self):
        self.stopped = True
        if self.check_runner is not None:
            self.check_runner.stop()
