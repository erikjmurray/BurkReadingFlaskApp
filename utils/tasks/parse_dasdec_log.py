import os
import re
from typing import List, Tuple
from utils.eas_parse.AllTests import AllTests
from utils.eas_parse.DasdecLogParser import DasdecLogParser


def read_from_file(filename: str) -> str:
    """ Given filename load data """
    with open(filename, 'r') as f:
        content = f.read()
    return content


def get_dasdec_name_from_file_name(file: str) -> str:
    pattern = r'^\d{8}_\d{4}_([^_]+)_'
    match = re.match(pattern, file)

    if match:
        return match.group(1)


def parse_dasdec_logs() -> List[Tuple[str, AllTests]]:
    """
    Grabs all files in EAS LOGS folder and parses data into lists of tests
    """
    eas_log_dir = os.path.join(os.getcwd(), 'eas_logs')
    files = os.listdir(eas_log_dir)

    all_eas_data = []
    for file in files:
        content = read_from_file(os.path.join(eas_log_dir, file))
        dasdec_name = get_dasdec_name_from_file_name(file)
        all_tests = DasdecLogParser(content).parse_content()
        # id of decoded test is the same as forwarded test.
        # sort and return only pertinent tests
        # orig, fwd, decoded(received)
        # note logs only include expired events
        # test_func(all_tests)
        all_eas_data.append((dasdec_name, all_tests))
    return all_eas_data


def test_func(all_tests: AllTests):
    forwarded_ids = [test.id for test in  all_tests.forwarded_tests]
    decoded_ids = [test.id for test in all_tests.decoded_tests]
    cap_ids = [test.id for test in all_tests.cap_eas_decoded_tests]
    net_ids = [test.id for test in all_tests.eas_net_decoded_tests]

    for test in forwarded_ids:
        if test in decoded_ids:
            print(f'Test {test} forwarded from Decoded')
        elif test in cap_ids:
            print(f'Test {test} forwarded from CAP')
        elif test in net_ids:
            print(f'Test {test} forwarded from NET')
        else:
            print(f'Where did test {test} come from?')

