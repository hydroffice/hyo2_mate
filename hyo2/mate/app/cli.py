import argparse
import json
import os

from hyo2.mate.lib.check_runner import CheckRunner
from hyo2.qax.lib.qa_json import QAJson


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help='Path to input QA JSON file', required=True)
    parser.add_argument(
        "-o", "--output", help='Path to output QA JSON file. If not provided \
        will be printed to stdout.', required=False)
    args = parser.parse_args()

    qajson_input = args.input
    if not os.path.isfile(qajson_input):
        raise RuntimeError(
            "QA JSON file does not exist {}".format(qajson_input))

    # most recent schema
    schema_path = QAJson.schema_paths()[0]

    # validate the provided QA JSON file against the JSON schema definition
    if not QAJson.validate_qa_json(qajson_input, schema_path):
        raise RuntimeError(
            "QA JSON is invalid {}".format(qajson_input))

    rawdatachecks = None
    output = None
    with open(qajson_input) as jsonfile:
        qajson = json.load(jsonfile)
        output = qajson
        rawdatachecks = qajson['qa']['raw_data']['checks']

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
