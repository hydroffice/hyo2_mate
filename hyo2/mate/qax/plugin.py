from typing import List, Dict, NoReturn

from hyo2.mate.lib.scan_utils import all_checks
from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType


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
            )
            check_refs.append(cr)
        return check_refs

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        print("Running Mate")
