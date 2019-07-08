import argparse
import json
import os

from hyo2.mate.lib.check_runner import CheckRunner
from hyo2.qax.lib.qa_json import QAJson


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help='Path to input QC JSON file', required=True)
    parser.add_argument(
        "-o", "--output", help='Path to output QC JSON file. If not provided \
        will be printed to stdout.', required=False)
    args = parser.parse_args()

    qcjson_input = args.input
    if not os.path.isfile(qcjson_input):
        raise RuntimeError(
            "QC JSON file does not exist {}".format(qcjson_input))

    # most recent schema
    schema_path = QAJson.schema_paths()[0]

    # validate the provided QC JSON file against the JSON schema definition
    if not QAJson.validate_qa_json(qcjson_input, schema_path):
        raise RuntimeError(
            "QC JSON is invalid {}".format(qcjson_input))

    rawdatachecks = None
    output = None
    with open(qcjson_input) as jsonfile:
        qcjson = json.load(jsonfile)
        output = qcjson
        rawdatachecks = qcjson['qa']['raw_data']['checks']

    checkrunner = CheckRunner(rawdatachecks)
    checkrunner.initialize()
    checkrunner.run_checks()

    output['qa']['raw_data']['checks'] = checkrunner.output
    if args.output is None:
        # If output not specified p[rint to std out
        print(json.dumps(output, indent=4))
    else:
        qajson_output = args.output
        with open(qajson_output, 'w') as jsonfileoutput:
            jsonfileoutput.write(json.dumps(output, indent=4))


if __name__ == '__main__':
    main()
