import argparse
import os
from hyo2.qax.lib.project import QAXProject


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-qcjson", help='Path to QC JSON file', required=True)
    args = parser.parse_args()

    qcjson_input = args.qcjson
    if not os.path.isfile(qcjson_input):
        raise RuntimeError(
            "QC JSON file does not exist {}".format(qcjson_input))

    # most recent schema
    schema_path = QAXProject.schema_paths()[0]

    # validate the provided QC JSON file against the JSON schema definition
    if not QAXProject.validate_qa_json(qcjson_input, schema_path):
        raise RuntimeError(
            "QC JSON is invalid {}".format(qcjson_input))

    # TODO
    # - use params and check definitions in JSON to run checks


if __name__ == '__main__':
    main()
